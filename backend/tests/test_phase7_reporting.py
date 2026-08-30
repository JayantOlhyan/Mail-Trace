import io
import json
import zipfile
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.reports.hashing import calculate_sha256, create_evidence_item
from app.reports.generator import ForensicReportGenerator
from app.reports.exporter import ReportExporter
from app.reports.demo import sih_demo_service


def test_sha256_evidence_hashing():
    data = {"sample": "evidence", "risk": 91}
    hash1 = calculate_sha256(data)
    hash2 = calculate_sha256(data)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex string length

    item = create_evidence_item(
        evidence_id="EVD-TEST-01",
        evidence_type="Raw Header",
        source="Parser",
        origin_phase="Phase 1",
        raw_content=data,
    )
    assert item.sha256_hash == hash1
    assert item.id == "EVD-TEST-01"


def test_report_schema_generation_and_versioning():
    generator = ForensicReportGenerator()
    report = generator.generate_report(
        case_id="CASE-2026-0042",
        investigation_id="EML-2026-8801",
        email_data={"id": "EML-2026-8801", "sender": "test@domain.com"},
        threat_assessment={"risk_score": 91, "classification": "PHISHING", "findings": []},
        header_forensics={"spf_status": "FAIL", "dkim_status": "FAIL", "dmarc_status": "FAIL"},
        infrastructure_data={"ip": "203.0.113.10", "asn": "AS12345"},
        graph_data={"nodes": [], "edges": []},
        version="1.0",
    )

    assert report.report_id == "RPT-2026-0042"
    assert report.case_id == "CASE-2026-0042"
    assert report.version == "1.0"
    assert report.evidence_count == 4
    assert len(report.evidence_inventory) == 4
    assert len(report.chain_of_custody) == 4


def test_machine_vs_analyst_findings_separation():
    generator = ForensicReportGenerator()
    report = generator.generate_report(
        case_id="CASE-2026-0042",
        investigation_id="EML-2026-8801",
        email_data={"id": "EML-2026-8801"},
        threat_assessment={"risk_score": 91, "classification": "PHISHING", "findings": []},
        header_forensics={"spf_status": "FAIL"},
        infrastructure_data={},
        graph_data={},
        analyst_decision="CONFIRMED PHISHING",
        case_status="ESCALATED",
        assigned_analyst="Analyst Jayant",
    )

    # Machine Findings
    assert report.machine_findings.ai_classification == "PHISHING"
    assert report.machine_findings.risk_score == 91

    # Analyst Findings
    assert report.analyst_findings.analyst_decision == "CONFIRMED PHISHING"
    assert report.analyst_findings.case_status == "ESCALATED"
    assert report.analyst_findings.assigned_analyst == "Analyst Jayant"


def test_pdf_json_and_zip_package_export():
    report = sih_demo_service.get_demo_report()
    exporter = ReportExporter()

    # JSON export
    json_str = exporter.export_json(report)
    assert "RPT-2026-0042" in json_str
    assert "EXECUTIVE SUMMARY" not in json_str  # JSON key is executive_summary

    # PDF export
    pdf_bytes = exporter.export_pdf(report)
    assert b"MAILTRACE FORENSIC REPORT" in pdf_bytes
    assert b"RPT-2026-0042" in pdf_bytes

    # ZIP package export
    zip_bytes = exporter.export_zip_package(report)
    assert len(zip_bytes) > 0

    # Unpack ZIP and verify manifest integrity
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert "report.pdf" in namelist
        assert "case.json" in namelist
        assert "email.json" in namelist

        manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
        assert manifest_data["case_id"] == "CASE-2026-0042"
        assert manifest_data["evidence_count"] == 6


@pytest.mark.asyncio
async def test_phase7_api_report_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # POST report generation
        res = await client.post("/api/v1/cases/CASE-2026-0042/reports")
        assert res.status_code == 200
        data = res.json()
        assert data["report_id"] == "RPT-2026-0042"

        # GET report metadata
        res_meta = await client.get("/api/v1/reports/RPT-2026-0042")
        assert res_meta.status_code == 200

        # GET PDF download
        res_pdf = await client.get("/api/v1/reports/RPT-2026-0042/pdf")
        assert res_pdf.status_code == 200
        assert res_pdf.headers["content-type"] == "application/pdf"

        # GET JSON download
        res_json = await client.get("/api/v1/reports/RPT-2026-0042/json")
        assert res_json.status_code == 200
        assert res_json.headers["content-type"] == "application/json"

        # GET ZIP evidence package download
        res_pkg = await client.get("/api/v1/reports/RPT-2026-0042/package")
        assert res_pkg.status_code == 200
        assert res_pkg.headers["content-type"] == "application/zip"

        # POST Demo Reset
        res_reset = await client.post("/api/v1/demo/reset")
        assert res_reset.status_code == 200
        assert res_reset.json()["status"] == "SUCCESS"
