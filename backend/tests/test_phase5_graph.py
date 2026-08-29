import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import engine, Base, AsyncSessionLocal
from app.ingestion.eml_ingestor import EmlIngestor
from app.forensics.service import Phase2ForensicsService
from app.threat.service import Phase3ThreatService
from app.enrichment.service import Phase4EnrichmentService
from app.graph.service import Phase5GraphService
from app.graph.normalizer import EntityNormalizer
from app.graph.suppression import CommonInfrastructureSuppression
from app.graph.traversal import GraphTraversalEngine

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

def test_entity_normalization():
    clean_d, disp_d = EntityNormalizer.normalize_domain("Example.COM.")
    assert clean_d == "example.com"
    assert disp_d == "Example.COM"

    clean_ip, disp_ip = EntityNormalizer.normalize_ip("  203.0.113.10  ")
    assert clean_ip == "203.0.113.10"

    clean_url, _ = EntityNormalizer.normalize_url("HTTPS://Login.Example.Com/auth/")
    assert clean_url == "https://login.example.com/auth"

def test_common_infrastructure_suppression():
    # Cloudflare ASN
    penalty = CommonInfrastructureSuppression.get_suppression_penalty("IP", "1.1.1.1", {"asn": "AS13335"})
    assert penalty == 0.15

    # Cloudflare Nameserver
    penalty_ns = CommonInfrastructureSuppression.get_suppression_penalty("NAMESERVER", "ns1.cloudflare.com", {})
    assert penalty_ns == 0.10

    # Custom Attacker Infrastructure
    penalty_custom = CommonInfrastructureSuppression.get_suppression_penalty("IP", "185.220.101.5", {"asn": "AS-CUSTOM"})
    assert penalty_custom == 1.0

@pytest.mark.asyncio
async def test_phase5_single_email_graph_construction():
    raw_bytes = get_fixture_bytes("bec_payment_request.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "bec_payment_request.eml")

    async with AsyncSessionLocal() as session:
        forensics = await Phase2ForensicsService.analyze_and_persist(canonical, session)
        threat = await Phase3ThreatService.analyze_and_persist(canonical, forensics, session)
        enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical, forensics, session)
        res = await Phase5GraphService.build_and_persist(canonical, forensics, threat, enrichment, session)

    assert len(res.nodes) > 0
    assert len(res.edges) > 0
    node_types = [n.node_type.value for n in res.nodes]
    assert "EMAIL" in node_types
    assert "SENDER" in node_types

@pytest.mark.asyncio
async def test_phase5_cross_email_entity_resolution():
    raw_bytes1 = get_fixture_bytes("bec_payment_request.eml")
    raw_bytes2 = get_fixture_bytes("credential_harvesting.eml")

    canonical1 = EmlIngestor.ingest_bytes(raw_bytes1, "bec_payment_request.eml")
    canonical2 = EmlIngestor.ingest_bytes(raw_bytes2, "credential_harvesting.eml")

    async with AsyncSessionLocal() as session:
        f1 = await Phase2ForensicsService.analyze_and_persist(canonical1, session)
        t1 = await Phase3ThreatService.analyze_and_persist(canonical1, f1, session)
        e1 = await Phase4EnrichmentService.enrich_and_persist(canonical1, f1, session)
        await Phase5GraphService.build_and_persist(canonical1, f1, t1, e1, session)

        f2 = await Phase2ForensicsService.analyze_and_persist(canonical2, session)
        t2 = await Phase3ThreatService.analyze_and_persist(canonical2, f2, session)
        e2 = await Phase4EnrichmentService.enrich_and_persist(canonical2, f2, session)
        res2 = await Phase5GraphService.build_and_persist(canonical2, f2, t2, e2, session)

    assert len(res2.nodes) > 0

@pytest.mark.asyncio
async def test_phase5_api_graph_endpoints():
    raw_bytes = get_fixture_bytes("bec_payment_request.eml")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload
        up_res = await client.post(
            "/api/v1/emails/upload",
            files={"file": ("bec_payment_request.eml", raw_bytes, "message/rfc822")}
        )
        assert up_res.status_code == 201
        email_id = up_res.json()["email_id"]

        # Graph
        g_res = await client.get(f"/api/v1/emails/{email_id}/graph")
        assert g_res.status_code == 200

        # Relationships
        r_res = await client.get(f"/api/v1/emails/{email_id}/relationships")
        assert r_res.status_code == 200

        # Timeline
        t_res = await client.get(f"/api/v1/emails/{email_id}/timeline")
        assert t_res.status_code == 200

        # Campaigns
        c_res = await client.get(f"/api/v1/emails/{email_id}/campaigns")
        assert c_res.status_code == 200

        # Clusters
        cl_res = await client.get(f"/api/v1/emails/{email_id}/clusters")
        assert cl_res.status_code == 200
