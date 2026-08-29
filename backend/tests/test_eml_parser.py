import os
import pytest
from app.parsing.eml_parser import EmlParser
from app.ingestion.eml_ingestor import EmlIngestor

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

def get_sample_path(filename: str) -> str:
    return os.path.join(SAMPLES_DIR, filename)

def test_legitimate_eml_parsing():
    sample_path = get_sample_path("legitimate.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    assert parsed.headers.from_address == "security@example.com"
    assert parsed.headers.from_name == "Security Team"
    assert parsed.headers.to_addresses == ["analyst@company.local"]
    assert parsed.headers.subject == "Q3 Security Audit Reminder"
    assert parsed.headers.reply_to == "security@example.com"
    assert len(parsed.headers.received_chain) == 2
    assert "https://internal.company.local/docs/security" in parsed.body.extracted_urls
    assert len(parsed.attachments) == 0
    assert parsed.sha256_hash is not None

def test_spoofed_eml_parsing():
    sample_path = get_sample_path("spoofed.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    assert parsed.headers.from_address == "john.doe@company-legit.com"
    assert parsed.headers.from_name == "CEO John Doe"
    assert parsed.headers.reply_to == "attacker-collector@phish-domain.xyz"
    assert parsed.headers.return_path == "bounce@evil-server.net"
    assert len(parsed.headers.received_chain) == 3
    
    # Verify Received hops order
    assert parsed.headers.received_chain[0].ip_address == "185.220.101.5"  # Earliest hop
    assert parsed.headers.received_chain[2].ip_address == "10.0.0.1"      # Latest gateway hop

    # Verify attachment metadata extraction & SHA-256 hash calculation
    assert len(parsed.attachments) == 1
    attachment = parsed.attachments[0]
    assert attachment.filename == "invoice_q3.exe"
    assert attachment.content_type == "application/octet-stream"
    assert len(attachment.sha256_hash) == 64  # SHA-256 hex string

    # Verify extracted URL
    assert "http://login.update-secure-bank.xyz/login" in parsed.body.extracted_urls

def test_malformed_and_sanitization():
    sample_path = get_sample_path("malformed.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    # HTML Sanitization check
    sanitized_html = parsed.body.html_sanitized
    assert "<script>" not in sanitized_html
    assert "<iframe" not in sanitized_html
    assert "javascript:" not in sanitized_html
    assert "Click Safe Link" in sanitized_html

    # Extracted URLs check
    assert "https://legit-site.com" in parsed.body.extracted_urls

def test_ingestor_size_limit():
    huge_bytes = b"A" * (26 * 1024 * 1024)  # 26MB
    with pytest.raises(ValueError, match="exceeds max limit"):
        EmlIngestor.ingest_bytes(huge_bytes)
