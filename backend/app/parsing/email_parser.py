import email
from email import policy
import hashlib
from typing import Tuple, List, Dict
from app.parsing.headers import HeaderParser
from app.parsing.received import ReceivedParser
from app.parsing.body import BodyExtractor
from app.parsing.attachments import AttachmentExtractor
from app.parsing.indicators import IndicatorExtractor
from app.schemas.canonical import (
    CanonicalEmailObject,
    EvidenceRef,
    ContentSchema,
    MetadataSchema,
)

class EmailParserEngine:
    """
    Main MIME & RFC 5322 Email Parser Engine for ThreatTrace AI.
    Converts raw .eml bytes into a fully populated CanonicalEmailObject schema.
    """

    @classmethod
    def parse_eml(cls, raw_bytes: bytes, evidence_id: str, filename: str) -> Tuple[CanonicalEmailObject, List[Tuple[str, bytes]]]:
        if not raw_bytes:
            raise ValueError("Cannot parse empty raw .eml payload")

        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        size_bytes = len(raw_bytes)

        msg = email.message_from_bytes(raw_bytes, policy=policy.default)
        email_id = f"eml_{sha256_hash[:16]}"

        # 1. Parse Headers & Identities
        identity, headers_schema, date_raw = HeaderParser.parse_headers(msg)

        # 2. Parse Received Hop Chain
        received_hops = ReceivedParser.parse_received_headers(msg)
        headers_schema.received = received_hops

        # 3. Extract Text & HTML Body
        text_body, html_body = BodyExtractor.extract_body(msg)
        content = ContentSchema(
            subject=msg.get("Subject", "(No Subject)"),
            text_body=text_body,
            html_body=html_body
        )

        # 4. Extract Attachments
        attachments, attachment_payloads = AttachmentExtractor.extract_attachments(msg)

        # 5. Extract Indicators (IPs, Domains, URLs, Email Addresses with Provenance)
        indicators = IndicatorExtractor.extract_all(
            identity=identity,
            received_hops=received_hops,
            text_body=text_body,
            html_body=html_body or "",
            raw_headers=headers_schema.raw
        )

        evidence_ref = EvidenceRef(
            evidence_id=evidence_id,
            filename=filename,
            sha256=sha256_hash,
            size_bytes=size_bytes
        )

        metadata = MetadataSchema(
            received_date=date_raw,
            parser_version="1.0.0"
        )

        canonical_object = CanonicalEmailObject(
            email_id=email_id,
            evidence=evidence_ref,
            identity=identity,
            content=content,
            headers=headers_schema,
            indicators=indicators,
            attachments=attachments,
            metadata=metadata
        )

        return canonical_object, attachment_payloads
