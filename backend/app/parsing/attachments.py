import os
import hashlib
import uuid
import email
from typing import List, Tuple
from app.schemas.canonical import AttachmentSchema
from app.ingestion.storage import EvidenceStorageHandler

class AttachmentExtractor:
    """
    Extracts attachment metadata and SHA-256 cryptographic hashes from email MIME parts.
    NEVER executes attachments or uses unsafe filenames directly (prevents path traversal like ../../../../etc/passwd).
    """

    @classmethod
    def extract_attachments(cls, msg: email.message.EmailMessage) -> Tuple[List[AttachmentSchema], List[Tuple[str, bytes]]]:
        attachments: List[AttachmentSchema] = []
        attachment_payloads: List[Tuple[str, bytes]] = []  # (attachment_id, raw_bytes)

        if not msg.is_multipart():
            return attachments, attachment_payloads

        att_counter = 1
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))
            filename = part.get_filename()

            if filename or "attachment" in content_disposition.lower() or "inline" in content_disposition.lower():
                payload_bytes = part.get_payload(decode=True)
                if payload_bytes is None:
                    continue

                raw_filename = filename or f"attachment_{att_counter}.bin"
                safe_filename = cls.sanitize_filename(raw_filename)
                
                content_type = part.get_content_type() or "application/octet-stream"
                size_bytes = len(payload_bytes)
                sha256_hash = hashlib.sha256(payload_bytes).hexdigest()
                content_id = str(part.get("Content-ID", "")).strip("<>") if part.get("Content-ID") else None
                disposition = "inline" if "inline" in content_disposition.lower() else "attachment"

                att_id = f"ATT-{sha256_hash[:12]}"

                # Save attachment binary payload safely using SHA-256 filename
                storage_path = EvidenceStorageHandler.save_attachment(payload_bytes, sha256_hash)

                attachments.append(AttachmentSchema(
                    attachment_id=att_id,
                    filename=safe_filename,
                    mime_type=content_type,
                    size_bytes=size_bytes,
                    content_id=content_id,
                    disposition=disposition,
                    sha256=sha256_hash
                ))

                attachment_payloads.append((att_id, payload_bytes))
                att_counter += 1

        return attachments, attachment_payloads

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Strips path traversal sequences (../, ..\\, etc.) and keeps only the base filename.
        """
        if not filename:
            return "unnamed_attachment"
        
        # Take basename to strip directory prefixes
        base = os.path.basename(filename.replace("\\", "/"))
        # Replace dangerous characters
        clean_name = "".join(c for c in base if c.isalnum() or c in "._- ")
        return clean_name.strip() or "unnamed_attachment"
