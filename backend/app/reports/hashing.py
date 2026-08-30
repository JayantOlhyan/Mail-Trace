import hashlib
import json
from datetime import datetime
from typing import Any, Union
from app.schemas.reports import EvidenceItemSchema


def calculate_sha256(data: Union[str, bytes, dict, list]) -> str:
    """
    Computes a cryptographic SHA-256 checksum for arbitrary evidence input.
    """
    if isinstance(data, (dict, list)):
        serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-[8]")
        return hashlib.sha256(serialized).hexdigest()
    elif isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    elif isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    else:
        return hashlib.sha256(str(data).encode("utf-8")).hexdigest()


def create_evidence_item(
    evidence_id: str,
    evidence_type: str,
    source: str,
    origin_phase: str,
    raw_content: Union[str, bytes, dict, list],
    case_id: str = None,
    captured_at: str = None,
) -> EvidenceItemSchema:
    """
    Constructs a validated EvidenceItemSchema with SHA-256 evidence hashing.
    """
    sha256 = calculate_sha256(raw_content)
    timestamp = captured_at or datetime.utcnow().isoformat() + "Z"
    
    return EvidenceItemSchema(
        id=evidence_id,
        evidence_type=evidence_type,
        source=source,
        captured_at=timestamp,
        origin_phase=origin_phase,
        sha256_hash=sha256,
        case_id=case_id,
    )
