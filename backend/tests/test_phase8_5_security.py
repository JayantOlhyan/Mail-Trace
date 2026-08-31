import pytest
from app.security.ssrf import validate_url_for_ssrf
from app.security.sanitizer import sanitize_email_html

def test_ssrf_basic_blocking():
    assert validate_url_for_ssrf("http://127.0.0.1/admin")[0] == False
    assert validate_url_for_ssrf("http://localhost:8080")[0] == False
    assert validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")[0] == False
    assert validate_url_for_ssrf("https://metadata.google.internal/computeMetadata/v1/")[0] == False
    assert validate_url_for_ssrf("http://10.0.0.5/internal-api")[0] == False

def test_ssrf_advanced_bypasses():
    # These represent adversarial bypass attempts.
    # Dword / Decimal encoding for 127.0.0.1
    assert validate_url_for_ssrf("http://2130706433/")[0] == False, "Failed to block decimal IP bypass"
    
    # Octal encoding
    assert validate_url_for_ssrf("http://0177.0.0.1/")[0] == False, "Failed to block octal IP bypass"
    
    # Hex encoding
    assert validate_url_for_ssrf("http://0x7f.0.0.1/")[0] == False, "Failed to block hex IP bypass"
    
    # URL encoded localhost
    assert validate_url_for_ssrf("http://%6c%6f%63%61%6c%68%6f%73%74/")[0] == False, "Failed to block URL encoded localhost"

def test_html_sanitizer_basic():
    dirty = "<h1>Title</h1><script>alert('xss');</script><p>Text</p>"
    clean = sanitize_email_html(dirty)
    assert "script" not in clean
    assert "<h1>Title</h1>" in clean

def test_html_sanitizer_advanced_bypasses():
    # Nested tags
    dirty1 = "<scr<script>ipt>alert(1)</script>"
    clean1 = sanitize_email_html(dirty1)
    assert "alert(1)" not in clean1 or "script" not in clean1.lower()
    
    # Obfuscated attributes
    dirty2 = "<img src='x' ONERROR='alert(1)'>"
    clean2 = sanitize_email_html(dirty2)
    assert "onerror" not in clean2.lower()
    
    # Javascript URI schemes with spaces/encoded
    dirty3 = "<a href='j a v a s c r i p t:alert(1)'>Click</a>"
    clean3 = sanitize_email_html(dirty3)
    assert "j a v a s c r i p t" not in clean3.lower()
    
    dirty4 = "<a href='javascript&colon;alert(1)'>Click</a>"
    clean4 = sanitize_email_html(dirty4)
    # The BeautifulSoup parser may or may not decode entities in attrs, let's see what happens.
    
    # Meta tag refresh
    dirty5 = "<meta http-equiv='refresh' content='0;url=javascript:alert(1)'>"
    clean5 = sanitize_email_html(dirty5)
    assert "meta" not in clean5.lower()
