import os
import pytest
from app.parsing.email_parser import EmailParserEngine

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def test_multiple_received_hops():
    path = os.path.join(FIXTURES_DIR, "multiple_received.eml")
    with open(path, "rb") as f:
        raw_bytes = f.read()

    canonical, _ = EmailParserEngine.parse_eml(raw_bytes, "EV-003", "multiple_received.eml")

    hops = canonical.headers.received
    assert len(hops) == 4

    # Order check: Hop 1 is earliest (client.origin.internal / 10.2.0.88)
    assert hops[0].hop_order == 1
    assert hops[0].source_hostname == "client.origin.internal"

    # Hop 4 is latest recipient gateway (gateway.company.local / 10.0.0.1)
    assert hops[3].hop_order == 4
    assert hops[3].source_hostname == "gateway.company.local"
