import io
import json
import zipfile
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.security.ssrf import validate_url_for_ssrf
from app.security.sanitizer import sanitize_email_html
from app.analysis.metrics import evaluate_dataset_classification_metrics


def test_ssrf_protection_validation():
    # Forbidden URLs
    safe, msg = validate_url_for_ssrf("http://127.0.0.1/admin")
    assert not safe
    assert "Forbidden" in msg

    safe, msg = validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")
    assert not safe

    safe, msg = validate_url_for_ssrf("http://10.0.0.1/internal")
    assert not safe

    safe, msg = validate_url_for_ssrf("ftp://example.com")
    assert not safe

    # Allowed public URL
    safe, msg = validate_url_for_ssrf("https://example.com/login")
    assert safe
    assert "validated successfully" in msg


def test_html_sanitizer_security():
    malicious_html = """
    <div>
        <h1>Welcome</h1>
        <script>alert('xss');</script>
        <iframe src="http://malicious.com"></iframe>
        <a href="javascript:alert(1)" onclick="stealCookies()">Click me</a>
        <img src="valid.jpg" onload="exploit()" />
    </div>
    """
    clean_html = sanitize_email_html(malicious_html)

    assert "<script>" not in clean_html
    assert "<iframe>" not in clean_html
    assert "onclick" not in clean_html
    assert "onload" not in clean_html
    assert "javascript:" not in clean_html
    assert "<h1>Welcome</h1>" in clean_html


def test_classification_metrics_evaluation():
    dataset = [
        {"email_id": "1", "expected_is_malicious": True, "predicted_is_malicious": True},
        {"email_id": "2", "expected_is_malicious": True, "predicted_is_malicious": True},
        {"email_id": "3", "expected_is_malicious": False, "predicted_is_malicious": False},
        {"email_id": "4", "expected_is_malicious": False, "predicted_is_malicious": True},  # FP
    ]
    res = evaluate_dataset_classification_metrics(dataset)
    assert res.total_samples == 4
    assert res.confusion_matrix.true_positives == 2
    assert res.confusion_matrix.true_negatives == 1
    assert res.confusion_matrix.false_positives == 1
    assert res.precision == 0.6667
    assert res.recall == 1.0


@pytest.mark.asyncio
async def test_e2e_full_investigation_and_export_pipeline():
    sample_eml = (
        "From: payroll-update@paypa1-support.com\r\n"
        "To: employee@target-org.com\r\n"
        "Subject: URGENT: Direct Deposit Verification\r\n"
        "Date: Sun, 30 Aug 2026 14:23:10 +0000\r\n"
        "Message-ID: <202608301423.8801@paypa1-support.com>\r\n"
        "Received: from mail.paypa1-support.com (203.0.113.10) by mta-01.relay-host.net\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n\r\n"
        "Please verify your payroll information immediately at http://verify-login.paypa1-support.com/auth"
    ).encode("utf-8")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health Probe
        health_res = await client.get("/api/v1/system/health")
        assert health_res.status_code == 200
        assert health_res.json()["status"] == "OK"

        # 2. Upload EML File
        files = {"file": ("test_phish.eml", sample_eml, "message/rfc822")}
        upload_res = await client.post("/api/v1/emails/upload", files=files)
        assert upload_res.status_code == 201
        upload_data = upload_res.json()
        email_id = upload_data["email_id"]
        assert email_id.startswith("eml_")

        # 3. Get Canonical Email
        get_res = await client.get(f"/api/v1/emails/{email_id}")
        assert get_res.status_code == 200
        assert get_res.json()["identity"]["from"][0]["address"] == "payroll-update@paypa1-support.com"

        # 4. Phase 2 Forensics
        forensic_res = await client.post(f"/api/v1/emails/{email_id}/forensics")
        assert forensic_res.status_code == 200
        assert len(forensic_res.json()["relay_analysis"]["hops"]) > 0

        # 5. Phase 3 Threat Assessment
        threat_res = await client.post(f"/api/v1/emails/{email_id}/threat-analysis")
        assert threat_res.status_code == 200
        assert threat_res.json()["risk"]["score"] >= 0

        # 6. Generate Case Report
        report_res = await client.post("/api/v1/cases/CASE-2026-0042/reports")
        assert report_res.status_code == 200
        report_data = report_res.json()
        assert report_data["report_id"] == "RPT-2026-0042"

        # 7. Export Evidence Package
        pkg_res = await client.get("/api/v1/reports/RPT-2026-0042/package")
        assert pkg_res.status_code == 200
        assert pkg_res.headers["content-type"] == "application/zip"

        # Unpack and verify SHA-256 manifest
        with zipfile.ZipFile(io.BytesIO(pkg_res.content), "r") as zf:
            namelist = zf.namelist()
            assert "manifest.json" in namelist
            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            assert manifest["case_id"] == "CASE-2026-0042"
            assert len(manifest["files"]) > 0
