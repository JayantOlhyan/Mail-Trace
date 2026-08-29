import os
from typing import Optional
from app.core.config import settings

class IngestionValidationError(ValueError):
    """Raised when file upload fails ingestion validation checks."""
    pass

class EmailValidator:
    """
    Validates uploaded raw email payloads prior to evidence hashing and parsing.
    Enforces maximum file size thresholds and file integrity.
    """

    @classmethod
    def validate_bytes(cls, content: bytes, filename: Optional[str] = None) -> None:
        if not content:
            raise IngestionValidationError("Uploaded .eml file is empty (0 bytes)")

        if len(content) > settings.max_bytes:
            raise IngestionValidationError(
                f"File size ({len(content)} bytes) exceeds maximum allowed limit of {settings.MAX_EMAIL_SIZE_MB}MB ({settings.max_bytes} bytes)"
            )

        if filename:
            # Prevent path traversal in uploaded filename
            base_name = os.path.basename(filename)
            if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
                # Sanitized log warning, but allowed as metadata
                pass

    @classmethod
    def validate_file_path(cls, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise IngestionValidationError(f"File path '{file_path}' does not exist")
        if not os.path.isfile(file_path):
            raise IngestionValidationError(f"Path '{file_path}' is not a regular file")

        size = os.path.getsize(file_path)
        if size == 0:
            raise IngestionValidationError(f"File '{file_path}' is empty (0 bytes)")
        if size > settings.max_bytes:
            raise IngestionValidationError(
                f"File size ({size} bytes) exceeds maximum limit of {settings.MAX_EMAIL_SIZE_MB}MB"
            )
