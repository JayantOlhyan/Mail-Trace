from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_v1_router
from app.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="ThreatTrace AI — Email Threat Detection & Forensic Intelligence API",
    description="ThreatTrace AI — Forensic Email Ingestion, Forensics, Intelligence & Reporting Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_v1_router, prefix="/api")

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": "ThreatTrace AI Email Ingestion & Forensic Engine",
        "version": "1.0.0"
    }
