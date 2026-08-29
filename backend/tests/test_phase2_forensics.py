import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base, AsyncSessionLocal
from app.ingestion.eml_ingestor import EmlIngestor
from app.forensics.service import Phase2ForensicsService

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

def get_fixture_bytes(filename: str) -> bytes:
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "rb") as f:
        return f.read()

@pytest.mark.asyncio
async def test_phase2_spf_pass_analysis():
    raw_bytes = get_fixture_bytes("spf_pass.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "spf_pass.eml")

    async with AsyncSessionLocal() as session:
        analysis = await Phase2ForensicsService.analyze_and_persist(canonical, session)

    assert analysis.authentication.spf.result == "PASS"
    assert analysis.authentication.spf.domain == "sender.com"
    assert len(analysis.timeline) >= 2

@pytest.mark.asyncio
async def test_phase2_spf_fail_analysis():
    raw_bytes = get_fixture_bytes("spf_fail.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "spf_fail.eml")

    async with AsyncSessionLocal() as session:
        analysis = await Phase2ForensicsService.analyze_and_persist(canonical, session)

    assert analysis.authentication.spf.result == "FAIL"
    rule_ids = [f.rule_id for f in analysis.findings]
    assert "HDR007" in rule_ids  # Unexpected authentication result rule

@pytest.mark.asyncio
async def test_phase2_replyto_mismatch_rule():
    raw_bytes = get_fixture_bytes("replyto_mismatch.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "replyto_mismatch.eml")

    async with AsyncSessionLocal() as session:
        analysis = await Phase2ForensicsService.analyze_and_persist(canonical, session)

    rule_ids = [f.rule_id for f in analysis.findings]
    assert "HDR001" in rule_ids  # From/Reply-To mismatch
    hdr001_finding = next(f for f in analysis.findings if f.rule_id == "HDR001")
    assert hdr001_finding.severity == "medium"
    assert hdr001_finding.confidence == 0.98
    assert len(hdr001_finding.evidence) == 2

@pytest.mark.asyncio
async def test_phase2_timestamp_anomaly_rule():
    raw_bytes = get_fixture_bytes("timestamp_anomaly.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "timestamp_anomaly.eml")

    async with AsyncSessionLocal() as session:
        analysis = await Phase2ForensicsService.analyze_and_persist(canonical, session)

    rule_ids = [f.rule_id for f in analysis.findings]
    assert "HDR004" in rule_ids  # Received timestamp sequence anomaly rule

@pytest.mark.asyncio
async def test_phase2_api_forensics_endpoints():
    raw_bytes = get_fixture_bytes("replyto_mismatch.eml")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload first
        up_res = await client.post(
            "/api/v1/emails/upload",
            files={"file": ("replyto_mismatch.eml", raw_bytes, "message/rfc822")}
        )
        assert up_res.status_code == 201
        email_id = up_res.json()["email_id"]

        # Fetch Forensics
        f_res = await client.get(f"/api/v1/emails/{email_id}/forensics")
        assert f_res.status_code == 200
        assert f_res.json()["email_id"] == email_id

        # Fetch Authentication Matrix
        auth_res = await client.get(f"/api/v1/emails/{email_id}/authentication")
        assert auth_res.status_code == 200

        # Fetch Findings
        find_res = await client.get(f"/api/v1/emails/{email_id}/findings")
        assert find_res.status_code == 200
        assert any(f["rule_id"] == "HDR001" for f in find_res.json())

        # Fetch Timeline
        tl_res = await client.get(f"/api/v1/emails/{email_id}/timeline")
        assert tl_res.status_code == 200

        # Fetch Trace
        trace_res = await client.get(f"/api/v1/emails/{email_id}/trace")
        assert trace_res.status_code == 200
