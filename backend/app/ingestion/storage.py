import os
import uuid
from app.core.config import settings

class EvidenceStorageHandler:
    """
    Handles immutable, safe evidence storage.
    Prevents path traversal attacks (e.g. ../../../../etc/passwd) by generating safe internal storage paths.
    """

    @classmethod
    def save_evidence(cls, raw_bytes: bytes, sha256_hash: str) -> str:
        """
        Saves raw bytes into EVIDENCE_STORAGE_PATH using the SHA-256 hash as the filename.
        Returns the absolute storage path.
        """
        os.makedirs(settings.EVIDENCE_STORAGE_PATH, exist_ok=True)
        safe_filename = f"{sha256_hash}.eml"
        file_path = os.path.join(settings.EVIDENCE_STORAGE_PATH, safe_filename)

        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(raw_bytes)

        return file_path

    @classmethod
    def save_attachment(cls, raw_bytes: bytes, attachment_sha256: str) -> str:
        """
        Saves attachment payload safely using SHA-256 hash to prevent path traversal executable threats.
        """
        att_dir = os.path.join(settings.EVIDENCE_STORAGE_PATH, "attachments")
        os.makedirs(att_dir, exist_ok=True)
        safe_filename = f"{attachment_sha256}.bin"
        file_path = os.path.join(att_dir, safe_filename)

        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(raw_bytes)

        return file_path
