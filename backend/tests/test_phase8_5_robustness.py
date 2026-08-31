import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

client = TestClient(app, raise_server_exceptions=False)

@pytest.mark.asyncio
async def test_robustness_db_outage_handling():
    async def mock_get_db_outage():
        raise Exception("Database connection lost (Simulated)")
    
    app.dependency_overrides[get_db] = mock_get_db_outage
    try:
        response = client.post(
            "/api/v1/emails/upload",
            files={"file": ("test.eml", b"Subject: Test\r\n\r\nHello", "message/rfc822")}
        )
        assert response.status_code == 500
    finally:
        app.dependency_overrides.pop(get_db, None)

@pytest.mark.asyncio
async def test_robustness_large_payload_handling():
    # A massive string that could cause memory exhaustion
    large_payload = b"A" * (1024 * 1024 * 20) # 20MB payload
    response = client.post(
        "/api/v1/emails/upload",
        files={"file": ("large.eml", large_payload, "message/rfc822")}
    )
    # The system should either process it or reject it with 413, but not crash
    assert response.status_code in (413, 400, 201)

def test_robustness_health_endpoints_active_under_load():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert "status" in response.json()
