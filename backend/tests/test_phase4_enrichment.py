import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import engine, Base, AsyncSessionLocal
from app.ingestion.eml_ingestor import EmlIngestor
from app.forensics.service import Phase2ForensicsService
from app.enrichment.service import Phase4EnrichmentService
from app.enrichment.ip_classifier import IPClassifier
from app.enrichment.schemas import IPClassificationEnum
from app.enrichment.cache import IntelligenceCache

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    IntelligenceCache.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

def get_fixture_bytes(filename: str) -> bytes:
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "rb") as f:
        return f.read()

def test_ip_classification_ipv4_and_ipv6():
    # Public IPv4
    assert IPClassifier.classify("8.8.8.8") == IPClassificationEnum.PUBLIC
    assert IPClassifier.classify("1.1.1.1") == IPClassificationEnum.PUBLIC

    # Private IPv4
    assert IPClassifier.classify("10.0.0.1") == IPClassificationEnum.PRIVATE
    assert IPClassifier.classify("192.168.1.1") == IPClassificationEnum.PRIVATE
    assert IPClassifier.classify("172.16.0.1") == IPClassificationEnum.PRIVATE

    # Loopback & Link Local
    assert IPClassifier.classify("127.0.0.1") == IPClassificationEnum.LOOPBACK
    assert IPClassifier.classify("169.254.1.1") == IPClassificationEnum.LINK_LOCAL

    # IPv6
    assert IPClassifier.classify("2001:4860:4860::8888") == IPClassificationEnum.PUBLIC
    assert IPClassifier.classify("::1") == IPClassificationEnum.LOOPBACK
    assert IPClassifier.classify("fe80::1") == IPClassificationEnum.LINK_LOCAL
    assert IPClassifier.classify("fc00::1") == IPClassificationEnum.PRIVATE

    # Invalid
    assert IPClassifier.classify("999.999.999.999") == IPClassificationEnum.INVALID
    assert IPClassifier.classify("not_an_ip") == IPClassificationEnum.INVALID

@pytest.mark.asyncio
async def test_phase4_enrichment_bec_email():
    raw_bytes = get_fixture_bytes("bec_payment_request.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "bec_payment_request.eml")

    async with AsyncSessionLocal() as session:
        forensics = await Phase2ForensicsService.analyze_and_persist(canonical, session)
        enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical, forensics, session)

    assert enrichment.status.value == "COMPLETED"
    assert len(enrichment.indicators) > 0
    assert len(enrichment.domain_intelligence) > 0

    # Verify attribution disclaimers present
    assert any("does NOT identify the attacker" in d for d in enrichment.disclaimers)

@pytest.mark.asyncio
async def test_phase4_probable_origin_calculation():
    raw_bytes = get_fixture_bytes("bec_payment_request.eml")
    canonical = EmlIngestor.ingest_bytes(raw_bytes, "bec_payment_request.eml")

    async with AsyncSessionLocal() as session:
        forensics = await Phase2ForensicsService.analyze_and_persist(canonical, session)
        enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical, forensics, session)

    origin = enrichment.probable_origin
    assert origin.disclaimer is not None
    assert "estimated infrastructure location" in origin.disclaimer
    assert len(origin.basis) > 0

@pytest.mark.asyncio
async def test_phase4_api_enrichment_endpoints():
    raw_bytes = get_fixture_bytes("credential_harvesting.eml")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload
        up_res = await client.post(
            "/api/v1/emails/upload",
            files={"file": ("credential_harvesting.eml", raw_bytes, "message/rfc822")}
        )
        assert up_res.status_code == 201
        email_id = up_res.json()["email_id"]

        # Infrastructure
        infra_res = await client.get(f"/api/v1/emails/{email_id}/infrastructure")
        assert infra_res.status_code == 200

        # Geolocation
        geo_res = await client.get(f"/api/v1/emails/{email_id}/geolocation")
        assert geo_res.status_code == 200
        assert "NOT the physical location" in geo_res.json()["disclaimer"]

        # Domains
        dom_res = await client.get(f"/api/v1/emails/{email_id}/domains")
        assert dom_res.status_code == 200

        # Reputation
        rep_res = await client.get(f"/api/v1/emails/{email_id}/reputation")
        assert rep_res.status_code == 200

        # Origin
        orig_res = await client.get(f"/api/v1/emails/{email_id}/origin")
        assert orig_res.status_code == 200
