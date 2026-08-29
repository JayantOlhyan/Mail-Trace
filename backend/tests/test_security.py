import os
import pytest
from app.parsing.attachments import AttachmentExtractor
from app.parsing.email_parser import EmailParserEngine

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def test_path_traversal_sanitization():
    path = os.path.join(FIXTURES_DIR, "path_traversal_attachment.eml")
    with open(path, "rb") as f:
        raw_bytes = f.read()

    canonical, _ = EmailParserEngine.parse_eml(raw_bytes, "EV-005", "path_traversal_attachment.eml")

    assert len(canonical.attachments) == 1
    sanitized_filename = canonical.attachments[0].filename
    assert ".." not in sanitized_filename
    assert "/" not in sanitized_filename
    assert sanitized_filename == "passwd"

def test_malformed_email_graceful_handling():
    malformed_bytes = b"From: Bad Syntax <bad\r\nHeader-No-Colon\r\n\r\nSome body"
    canonical, _ = EmailParserEngine.parse_eml(malformed_bytes, "EV-006", "malformed.eml")

    assert canonical.email_id is not None
    assert "Some body" in canonical.content.text_body
