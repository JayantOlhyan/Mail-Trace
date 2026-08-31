import email
from email import policy
from email.header import decode_header
from email.utils import parseaddr
import hashlib
import re
import uuid
from typing import Union, List, Tuple, Optional
from app.parsing.models import (
    ParsedEmail,
    HeaderData,
    BodyContent,
    AttachmentMetadata,
    ReceivedHop,
)
from app.parsing.sanitizer import HTMLSanitizer

class EmlParser:
    """
    Robust RFC 5322 MIME & Header Parser Engine for ThreatTrace AI.
    Parses raw .eml bytes or string payloads into structured ParsedEmail Pydantic objects.
    Extracts complete header metadata, Received hop chains, body text/HTML, and attachment hashes.
    """

    @classmethod
    def parse_bytes(cls, eml_bytes: bytes) -> ParsedEmail:
        if not eml_bytes:
            raise ValueError("Cannot parse empty .eml payload")

        sha256_hash = hashlib.sha256(eml_bytes).hexdigest()
        raw_size = len(eml_bytes)
        
        # Use Python's email policy default for RFC 5322 compliance
        msg = email.message_from_bytes(eml_bytes, policy=policy.default)
        
        return cls._parse_message(msg, raw_size, sha256_hash)

    @classmethod
    def parse_string(cls, eml_str: str) -> ParsedEmail:
        eml_bytes = eml_str.encode("utf-8", errors="replace")
        return cls.parse_bytes(eml_bytes)

    @classmethod
    def _parse_message(cls, msg: email.message.EmailMessage, raw_size: int, sha256_hash: str) -> ParsedEmail:
        email_id = f"msg_{sha256_hash[:16]}"

        # 1. Parse Headers
        headers = cls._extract_headers(msg)

        # 2. Parse Body & Attachments
        plain_text, html_raw, attachments = cls._extract_body_and_attachments(msg)

        # 3. Sanitize HTML & Extract URLs
        html_sanitized = HTMLSanitizer.sanitize(html_raw) if html_raw else None
        extracted_urls = HTMLSanitizer.extract_urls(html_raw or "", plain_text or "")

        body = BodyContent(
            plain_text=plain_text.strip(),
            html_raw=html_raw,
            html_sanitized=html_sanitized,
            extracted_urls=extracted_urls
        )

        return ParsedEmail(
            email_id=email_id,
            headers=headers,
            body=body,
            attachments=attachments,
            raw_eml_size=raw_size,
            sha256_hash=sha256_hash
        )

    @classmethod
    def _extract_headers(cls, msg: email.message.EmailMessage) -> HeaderData:
        from_str = str(msg.get("From", ""))
        from_name, from_address = cls._parse_email_address(from_str)

        to_str = str(msg.get("To", ""))
        to_addresses = [cls._parse_email_address(addr)[1] for addr in to_str.split(",") if addr.strip()]

        cc_str = str(msg.get("Cc", ""))
        cc_addresses = [cls._parse_email_address(addr)[1] for addr in cc_str.split(",") if addr.strip()]

        subject = str(msg.get("Subject", "(No Subject)"))
        date_raw = str(msg.get("Date", ""))
        message_id = str(msg.get("Message-ID", ""))
        
        reply_to_str = str(msg.get("Reply-To", ""))
        reply_to = cls._parse_email_address(reply_to_str)[1] if reply_to_str else None

        return_path_str = str(msg.get("Return-Path", ""))
        return_path = cls._parse_email_address(return_path_str)[1] if return_path_str else None

        # Parse Received hop headers
        received_chain = cls._parse_received_headers(msg.get_all("Received", []))

        # Collect custom extra headers
        standard_keys = {"from", "to", "cc", "subject", "date", "message-id", "reply-to", "return-path", "received"}
        custom_headers = {}
        for key, val in msg.items():
            if key.lower() not in standard_keys:
                custom_headers[str(key)] = str(val)

        return HeaderData(
            from_address=from_address or "unknown@domain.local",
            from_name=from_name,
            to_addresses=[a for a in to_addresses if a],
            cc_addresses=[a for a in cc_addresses if a],
            subject=subject,
            date_raw=date_raw,
            message_id=message_id,
            reply_to=reply_to,
            return_path=return_path,
            received_chain=received_chain,
            custom_headers=custom_headers
        )

    @classmethod
    def _parse_email_address(cls, addr_header: str) -> Tuple[Optional[str], str]:
        """Parses 'Display Name <user@domain.com>' into ('Display Name', 'user@domain.com')."""
        if not addr_header:
            return None, ""
        
        name, address = parseaddr(addr_header)
        display_name = name.strip() if name and name.strip() else None
        clean_address = address.strip().lower() if address else addr_header.strip().lower()
        return display_name, clean_address

    @classmethod
    def _parse_received_headers(cls, received_headers: List[str]) -> List[ReceivedHop]:
        hops = []
        ip_regex = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

        # Received headers are read from top (newest hop) to bottom (earliest hop)
        # Reverse list so hop_index 1 represents earliest sending hop
        reversed_headers = list(reversed(received_headers))

        for idx, header_val in enumerate(reversed_headers, start=1):
            val_str = str(header_val)
            
            # Extract IP from Received header string
            ip_match = ip_regex.search(val_str)
            extracted_ip = ip_match.group(0) if ip_match else None

            # Extract from host and by host if present
            from_match = re.search(r'from\s+([^\s]+)', val_str, re.IGNORECASE)
            by_match = re.search(r'by\s+([^\s]+)', val_str, re.IGNORECASE)

            from_host = from_match.group(1) if from_match else None
            by_host = by_match.group(1) if by_match else None

            hops.append(ReceivedHop(
                hop_index=idx,
                by_host=by_host,
                from_host=from_host,
                ip_address=extracted_ip,
                timestamp_raw=val_str.split(";")[-1].strip() if ";" in val_str else None
            ))

        return hops

    @classmethod
    def _extract_body_and_attachments(cls, msg: email.message.EmailMessage) -> Tuple[str, Optional[str], List[AttachmentMetadata]]:
        plain_text = ""
        html_raw = None
        attachments: List[AttachmentMetadata] = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                filename = part.get_filename()

                # If part has a filename or disposition is attachment, treat as attachment
                if filename or "attachment" in content_disposition.lower():
                    payload_bytes = part.get_payload(decode=True) or b""
                    att_filename = filename or f"attachment_{uuid.uuid4().hex[:8]}"
                    content_type = part.get_content_type()
                    att_size = len(payload_bytes)
                    att_hash = hashlib.sha256(payload_bytes).hexdigest()

                    attachments.append(AttachmentMetadata(
                        filename=att_filename,
                        content_type=content_type,
                        size_bytes=att_size,
                        sha256_hash=att_hash,
                        content_disposition=content_disposition or "attachment"
                    ))
                else:
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not plain_text:
                        payload = part.get_payload(decode=True)
                        if payload:
                            plain_text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    elif content_type == "text/html" and not html_raw:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_raw = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
                if content_type == "text/html":
                    html_raw = text
                else:
                    plain_text = text

        return plain_text, html_raw, attachments
