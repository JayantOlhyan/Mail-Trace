from typing import Union
from app.parsing.eml_parser import EmlParser
from app.parsing.models import ParsedEmail

class EmlIngestor:
    """
    Ingestion Handler for MailTrace.
    Enforces payload size limits (25MB threat model threshold) and coordinates parsing.
    """
    MAX_PAYLOAD_SIZE = 25 * 1024 * 1024  # 25MB

    @classmethod
    def ingest_bytes(cls, eml_bytes: bytes) -> ParsedEmail:
        if len(eml_bytes) > cls.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload size ({len(eml_bytes)} bytes) exceeds max limit of {cls.MAX_PAYLOAD_SIZE} bytes (25MB)")

        return EmlParser.parse_bytes(eml_bytes)

    @classmethod
    def ingest_file_path(cls, file_path: str) -> ParsedEmail:
        with open(file_path, "rb") as f:
            content = f.read()
        return cls.ingest_bytes(content)
