import os
import pytest
from app.parsing.indicators import IndicatorExtractor
from app.parsing.email_parser import EmailParserEngine

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def test_ip_classification():
    cat_pub, v4 = IndicatorExtractor.classify_ip("8.8.8.8")
    assert cat_pub == "public"
    assert v4 == "IPv4"

    cat_priv, _ = IndicatorExtractor.classify_ip("192.168.1.1")
    assert cat_priv == "private"

    cat_loop, _ = IndicatorExtractor.classify_ip("127.0.0.1")
    assert cat_loop == "loopback"

    cat_v6, v6 = IndicatorExtractor.classify_ip("2001:db8:85a3::8a2e:370:7334")
    assert v6 == "IPv6"

def test_deceptive_links_extraction():
    path = os.path.join(FIXTURES_DIR, "deceptive_html_links.eml")
    with open(path, "rb") as f:
        raw_bytes = f.read()

    canonical, _ = EmailParserEngine.parse_eml(raw_bytes, "EV-004", "deceptive_html_links.eml")

    urls = canonical.indicators.urls
    url_strings = [u.raw_url for u in urls]

    assert "http://evil-phish-collector.com/login" in url_strings
    assert "https://secure.mybank.com/login" in url_strings
