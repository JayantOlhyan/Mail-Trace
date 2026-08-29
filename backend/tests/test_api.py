import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json()["status"] == "online"

@pytest.mark.asyncio
async def test_upload_email_endpoint():
    sample_path = os.path.join(FIXTURES_DIR, "plain_text.eml")
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/emails/upload",
            files={"file": ("plain_text.eml", file_bytes, "message/rfc822")}
        )
        if res.status_code != 201:
            print("ERROR DETAIL:", res.status_code, res.json())
        assert res.status_code == 201
        data = res.json()
        assert "email_id" in data
        assert data["evidence"]["sha256"] is not None
        assert data["content"]["subject"] == "Simple Plain Text Email"

        email_id = data["email_id"]
        # Fetch email by ID
        get_res = await client.get(f"/api/v1/emails/{email_id}")
        assert get_res.status_code == 200
        assert get_res.json()["email_id"] == email_id

        # Fetch headers
        hdr_res = await client.get(f"/api/v1/emails/{email_id}/headers")
        assert hdr_res.status_code == 200
        assert "From" in hdr_res.json()["raw"]

        # Fetch indicators
        ind_res = await client.get(f"/api/v1/emails/{email_id}/indicators")
        assert ind_res.status_code == 200
        assert len(ind_res.json()["domains"]) >= 1
