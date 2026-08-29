import hashlib
import uuid
from typing import Tuple

class EvidenceMetadata:
    """
    Computes cryptographic SHA-256 hash and generates immutable Evidence tracking identifiers (EV-xxxxxx).
    """

    @classmethod
    def process_payload(cls, raw_bytes: bytes, filename: str) -> Tuple[str, str, int]:
        """
        Returns (evidence_id, sha256_hash, size_bytes).
        The SHA-256 hash is calculated from the exact original bytes.
        """
        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        size_bytes = len(raw_bytes)
        evidence_id = f"EV-{sha256_hash[:12]}"
        return evidence_id, sha256_hash, size_bytes
