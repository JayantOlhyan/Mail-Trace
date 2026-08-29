import os
import pytest
from app.ingestion.validator import EmailValidator, IngestionValidationError
from app.ingestion.evidence import EvidenceMetadata
from app.ingestion.storage import EvidenceStorageHandler

def test_evidence_hashing():
    raw_payload = b"From: test@example.com\r\nSubject: Test\r\n\r\nHello World"
    evidence_id, sha256_hash, size_bytes = EvidenceMetadata.process_payload(raw_payload, "test.eml")

    assert evidence_id.startswith("EV-")
    assert len(sha256_hash) == 64
    assert size_bytes == len(raw_payload)

def test_safe_evidence_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.EVIDENCE_STORAGE_PATH", str(tmp_path))

    raw_payload = b"Sample Raw EML Content"
    evidence_id, sha256_hash, _ = EvidenceMetadata.process_payload(raw_payload, "suspicious.eml")

    stored_path = EvidenceStorageHandler.save_evidence(raw_payload, sha256_hash)

    assert os.path.exists(stored_path)
    with open(stored_path, "rb") as f:
        assert f.read() == raw_payload

def test_oversized_validation_rejection(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.MAX_EMAIL_SIZE_MB", 1)
    huge_bytes = b"X" * (2 * 1024 * 1024)  # 2MB > 1MB limit

    with pytest.raises(IngestionValidationError, match="exceeds maximum allowed limit"):
        EmailValidator.validate_bytes(huge_bytes)
