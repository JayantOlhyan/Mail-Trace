import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ingestion.validator import EmailValidator
from app.ingestion.evidence import EvidenceMetadata
from app.ingestion.storage import EvidenceStorageHandler
from app.parsing.email_parser import EmailParserEngine
from app.schemas.canonical import CanonicalEmailObject
from app.models.db import (
    EvidenceTable,
    EmailTable,
    EmailAddressTable,
    ReceivedHeaderTable,
    URLTable,
    AttachmentTable,
)

class EmlIngestionPipeline:
    """
    Complete Phase 1 Ingestion Pipeline:
    Upload -> Validate -> SHA-256 Hashing -> Safe Storage -> MIME Parse -> Canonical Object -> DB Persistence
    """

    @classmethod
    def ingest_bytes(cls, raw_bytes: bytes, filename: str = "raw_sample.eml") -> CanonicalEmailObject:
        EmailValidator.validate_bytes(raw_bytes, filename)
        evidence_id, sha256_hash, _ = EvidenceMetadata.process_payload(raw_bytes, filename)
        canonical_obj, _ = EmailParserEngine.parse_eml(raw_bytes, evidence_id, filename)
        return canonical_obj

    @classmethod
    def ingest_file_path(cls, file_path: str) -> CanonicalEmailObject:
        EmailValidator.validate_file_path(file_path)
        with open(file_path, "rb") as f:
            content = f.read()
        filename = os.path.basename(file_path)
        return cls.ingest_bytes(content, filename)

    @classmethod
    async def process_upload(cls, raw_bytes: bytes, filename: str, db: AsyncSession) -> CanonicalEmailObject:
        # 1. Validate Upload
        EmailValidator.validate_bytes(raw_bytes, filename)

        # 2. Calculate Evidence SHA-256 and ID
        evidence_id, sha256_hash, size_bytes = EvidenceMetadata.process_payload(raw_bytes, filename)

        # 3. Store Immutable Original Raw File
        storage_path = EvidenceStorageHandler.save_evidence(raw_bytes, sha256_hash)

        # 4. Check if evidence already persisted in DB
        existing_evidence = await db.get(EvidenceTable, evidence_id)
        if not existing_evidence:
            evidence_record = EvidenceTable(
                id=evidence_id,
                sha256=sha256_hash,
                filename=filename,
                size_bytes=size_bytes,
                storage_path=storage_path
            )
            db.add(evidence_record)
            await db.flush()

        # 5. Parse MIME Payload into Canonical Email Object
        canonical_object, attachment_payloads = EmailParserEngine.parse_eml(raw_bytes, evidence_id, filename)

        # 6. Persist to PostgreSQL via SQLAlchemy 2.x
        existing_email = await db.get(EmailTable, canonical_object.email_id)
        if not existing_email:
            email_record = EmailTable(
                id=canonical_object.email_id,
                evidence_id=evidence_id,
                message_id=canonical_object.identity.message_id,
                subject=canonical_object.content.subject,
                text_body=canonical_object.content.text_body,
                html_body=canonical_object.content.html_body,
                raw_headers_json=canonical_object.headers.raw
            )
            db.add(email_record)
            await db.flush()

            # Save Email Addresses
            for role_name, addr_objs in [
                ("from", canonical_object.identity.from_),
                ("to", canonical_object.identity.to),
                ("cc", canonical_object.identity.cc),
                ("bcc", canonical_object.identity.bcc),
                ("reply_to", canonical_object.identity.reply_to),
            ]:
                for addr in addr_objs:
                    db.add(EmailAddressTable(
                        email_id=canonical_object.email_id,
                        address=addr.address,
                        display_name=addr.display_name,
                        domain=addr.domain,
                        role=role_name
                    ))

            if canonical_object.identity.return_path:
                rp_domain = canonical_object.identity.return_path.split("@")[-1] if "@" in canonical_object.identity.return_path else ""
                db.add(EmailAddressTable(
                    email_id=canonical_object.email_id,
                    address=canonical_object.identity.return_path,
                    display_name=None,
                    domain=rp_domain,
                    role="return_path"
                ))

            # Save Received Headers
            for hop in canonical_object.headers.received:
                db.add(ReceivedHeaderTable(
                    email_id=canonical_object.email_id,
                    hop_order=hop.hop_order,
                    source_hostname=hop.source_hostname,
                    source_ip=hop.source_ip,
                    destination=hop.destination,
                    protocol=hop.protocol,
                    timestamp=hop.timestamp,
                    raw_value=hop.raw_value
                ))

            # Save URLs
            for url in canonical_object.indicators.urls:
                db.add(URLTable(
                    email_id=canonical_object.email_id,
                    raw_url=url.raw_url,
                    normalized_url=url.normalized_url,
                    scheme=url.scheme,
                    hostname=url.hostname,
                    port=url.port,
                    path=url.path,
                    source_context=url.source_context
                ))

            # Save Attachments
            for att in canonical_object.attachments:
                att_storage_path = os.path.join(cls._get_att_dir(), f"{att.sha256}.bin")
                db.add(AttachmentTable(
                    id=att.attachment_id,
                    email_id=canonical_object.email_id,
                    filename=att.filename,
                    mime_type=att.mime_type,
                    size_bytes=att.size_bytes,
                    sha256=att.sha256,
                    content_id=att.content_id,
                    disposition=att.disposition,
                    storage_path=att_storage_path
                ))

            await db.commit()

        return canonical_object

    @classmethod
    def _get_att_dir(cls) -> str:
        from app.core.config import settings
        return os.path.join(settings.EVIDENCE_STORAGE_PATH, "attachments")

EmlIngestor = EmlIngestionPipeline
