import os
import pytest
from app.parsing.email_parser import EmailParserEngine

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def get_fixture_path(filename: str) -> str:
    return os.path.join(FIXTURES_DIR, filename)

def test_plain_text_parsing():
    path = get_fixture_path("plain_text.eml")
    with open(path, "rb") as f:
        raw_bytes = f.read()

    canonical, _ = EmailParserEngine.parse_eml(raw_bytes, "EV-001", "plain_text.eml")

    assert canonical.identity.from_[0].address == "sender@example.com"
    assert canonical.identity.to[0].address == "recipient@company.local"
    assert canonical.content.subject == "Simple Plain Text Email"
    assert "This is a simple plain text email body." in canonical.content.text_body
    assert canonical.content.html_body is None

def test_multipart_alternative_parsing():
    path = get_fixture_path("multipart_alternative.eml")
    with open(path, "rb") as f:
        raw_bytes = f.read()

    canonical, _ = EmailParserEngine.parse_eml(raw_bytes, "EV-002", "multipart_alternative.eml")

    assert canonical.identity.from_[0].display_name == "Marketing Team"
    assert canonical.identity.from_[0].address == "marketing@brand.com"
    assert "Read our weekly newsletter" in canonical.content.text_body
    assert "<html><body>" in canonical.content.html_body
