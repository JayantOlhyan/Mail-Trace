import os
import pytest
from app.ingestion.eml_ingestor import EmlIngestor
from app.parsing.sanitizer import HTMLSanitizer

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

def get_sample_path(filename: str) -> str:
    return os.path.join(SAMPLES_DIR, filename)

def test_legitimate_eml_parsing():
    sample_path = get_sample_path("legitimate.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    assert parsed.identity.from_[0].address == "security@example.com"
    assert parsed.identity.from_[0].display_name == "Security Team"
    assert parsed.identity.to[0].address == "analyst@company.local"
    assert parsed.content.subject == "Q3 Security Audit Reminder"
    assert parsed.identity.reply_to[0].address == "security@example.com"
    assert len(parsed.headers.received) == 2
    
    extracted_urls = [u.raw_url for u in parsed.indicators.urls]
    assert "https://internal.company.local/docs/security" in extracted_urls
    assert len(parsed.attachments) == 0
    assert parsed.evidence.sha256 is not None

def test_spoofed_eml_parsing():
    sample_path = get_sample_path("spoofed.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    assert parsed.identity.from_[0].address == "john.doe@company-legit.com"
    assert parsed.identity.from_[0].display_name == "CEO John Doe"
    assert parsed.identity.reply_to[0].address == "attacker-collector@phish-domain.xyz"
    assert parsed.identity.return_path == "bounce@evil-server.net"
    assert len(parsed.headers.received) == 3
    
    # Verify Received hops order
    assert parsed.headers.received[0].source_ip == "185.220.101.5"  # Earliest hop
    assert parsed.headers.received[2].source_ip == "10.0.0.1"       # Latest gateway hop

    # Verify attachment metadata extraction & SHA-256 hash calculation
    assert len(parsed.attachments) == 1
    attachment = parsed.attachments[0]
    assert attachment.filename == "invoice_q3.exe"
    assert attachment.mime_type == "application/octet-stream"
    assert len(attachment.sha256) == 64  # SHA-256 hex string

    # Verify extracted URL
    extracted_urls = [u.raw_url for u in parsed.indicators.urls]
    assert "http://login.update-secure-bank.xyz/login" in extracted_urls

def test_malformed_and_sanitization():
    sample_path = get_sample_path("malformed.eml")
    parsed = EmlIngestor.ingest_file_path(sample_path)

    # HTML Sanitization check
    sanitized_html = HTMLSanitizer.sanitize(parsed.content.html_body) if parsed.content.html_body else ""
    assert "<script>" not in sanitized_html
    assert "<iframe" not in sanitized_html
    assert "javascript:" not in sanitized_html
    assert "Click Safe Link" in sanitized_html

    # Extracted URLs check
    extracted_urls = [u.raw_url for u in parsed.indicators.urls]
    assert "https://legit-site.com" in extracted_urls

def test_ingestor_size_limit():
    huge_bytes = b"A" * (26 * 1024 * 1024)  # 26MB
    with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
        EmlIngestor.ingest_bytes(huge_bytes)
