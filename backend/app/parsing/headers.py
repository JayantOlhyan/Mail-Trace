import email
from email.header import decode_header, make_header
from email.utils import parseaddr
from typing import Dict, List, Tuple, Optional
from app.schemas.canonical import AddressObject, IdentitySchema, HeadersSchema

class HeaderParser:
    """
    Parses and normalizes email headers while preserving raw headers and custom X-headers.
    """

    STANDARD_HEADERS = {
        "from", "to", "cc", "bcc", "reply-to", "return-path", "subject", "date",
        "message-id", "in-reply-to", "references", "received", "authentication-results",
        "received-spf", "dkim-signature", "arc-seal", "arc-message-signature",
        "arc-authentication-results", "x-originating-ip", "x-mailer", "user-agent", "x-received"
    }

    AUTHENTICATION_HEADER_KEYS = {
        "authentication-results", "received-spf", "dkim-signature",
        "arc-seal", "arc-message-signature", "arc-authentication-results"
    }

    @classmethod
    def parse_headers(cls, msg: email.message.EmailMessage) -> Tuple[IdentitySchema, HeadersSchema, Optional[str]]:
        raw_headers: Dict[str, str] = {}
        auth_headers: Dict[str, str] = {}
        other_headers: Dict[str, str] = {}

        for key, val in msg.items():
            k_str = str(key)
            v_str = cls.decode_header_text(str(val))
            raw_headers[k_str] = v_str

            k_lower = k_str.lower()
            if k_lower in cls.AUTHENTICATION_HEADER_KEYS:
                auth_headers[k_str] = v_str
            elif k_lower not in cls.STANDARD_HEADERS:
                other_headers[k_str] = v_str

        # Decode Subject
        subject = cls.decode_header_text(str(msg.get("Subject", "(No Subject)")))
        date_raw = str(msg.get("Date", "")) if msg.get("Date") else None
        message_id = str(msg.get("Message-ID", "")) if msg.get("Message-ID") else None

        # Parse Identities
        from_list = cls._parse_address_header(msg.get_all("From", []))
        to_list = cls._parse_address_header(msg.get_all("To", []))
        cc_list = cls._parse_address_header(msg.get_all("Cc", []))
        bcc_list = cls._parse_address_header(msg.get_all("Bcc", []))
        reply_to_list = cls._parse_address_header(msg.get_all("Reply-To", []))

        return_path_str = str(msg.get("Return-Path", "")) if msg.get("Return-Path") else None
        return_path = cls.parse_single_address(return_path_str).address if return_path_str else None

        identity = IdentitySchema(
            message_id=message_id,
            from_=from_list,
            to=to_list,
            cc=cc_list,
            bcc=bcc_list,
            reply_to=reply_to_list,
            return_path=return_path
        )

        headers_schema = HeadersSchema(
            raw=raw_headers,
            received=[],  # Populated by ReceivedParser
            authentication_headers=auth_headers,
            other=other_headers
        )

        return identity, headers_schema, date_raw

    @classmethod
    def decode_header_text(cls, text: str) -> str:
        if not text:
            return ""
        try:
            return str(make_header(decode_header(text)))
        except Exception:
            return text

    @classmethod
    def _parse_address_header(cls, header_vals: List[str]) -> List[AddressObject]:
        results = []
        for val in header_vals:
            if not val:
                continue
            decoded_val = cls.decode_header_text(str(val))
            for chunk in decoded_val.split(","):
                chunk = chunk.strip()
                if chunk:
                    obj = cls.parse_single_address(chunk)
                    if obj.address:
                        results.append(obj)
        return results

    @classmethod
    def parse_single_address(cls, addr_str: str) -> AddressObject:
        if not addr_str:
            return AddressObject(display_name=None, address="", domain="")

        name, address = parseaddr(addr_str)
        clean_addr = address.strip().lower() if address else addr_str.strip().lower()

        # Strip surrounding brackets if present
        clean_addr = clean_addr.lstrip("<").rstrip(">").strip()
        domain = clean_addr.split("@")[-1] if "@" in clean_addr else ""

        display_name = name.strip() if name and name.strip() else None

        return AddressObject(
            display_name=display_name,
            address=clean_addr,
            domain=domain
        )
