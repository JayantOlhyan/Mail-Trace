from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.db import EmailTable
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.schemas.threat import Phase3ThreatAnalysisResponse
from app.enrichment.schemas import (
    Phase4EnrichmentResponse,
    IPIntelligenceSchema,
    DomainIntelligenceSchema,
    ReputationIntelligenceSchema,
    ProbableOriginSchema,
)
from app.parsing.email_parser import EmailParserEngine
from app.forensics.service import Phase2ForensicsService
from app.threat.service import Phase3ThreatService
from app.enrichment.service import Phase4EnrichmentService

router = APIRouter(prefix="/emails", tags=["Infrastructure Intelligence & Enrichment"])

async def _get_canonical_from_db(email_id: str, db: AsyncSession) -> CanonicalEmailObject:
    stmt = select(EmailTable).options(selectinload(EmailTable.evidence)).where(EmailTable.id == email_id)
    email_record = (await db.execute(stmt)).scalar_one_or_none()
    if not email_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email ID {email_id} not found")

    evidence_path = email_record.evidence.storage_path
    with open(evidence_path, "rb") as f:
        raw_bytes = f.read()

    canonical_obj, _ = EmailParserEngine.parse_eml(raw_bytes, email_record.evidence_id, email_record.evidence.filename)
    return canonical_obj

@router.post("/{email_id}/enrichment", response_model=Phase4EnrichmentResponse, status_code=status.HTTP_200_OK)
async def enrich_email_infrastructure(email_id: str, db: AsyncSession = Depends(get_db)):
    """Triggers or retrieves Phase 4 Infrastructure Intelligence & Enrichment."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    return await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)

@router.get("/{email_id}/enrichment", response_model=Phase4EnrichmentResponse)
async def get_email_enrichment(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves complete Phase 4 enrichment response JSON object."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    return await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)

@router.get("/{email_id}/infrastructure", response_model=List[IPIntelligenceSchema])
async def get_email_ip_infrastructure(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves IP network intelligence, ASN, and anonymization flags."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    return enrichment.ip_intelligence

@router.get("/{email_id}/geolocation", response_model=Dict[str, Any])
async def get_email_geolocation(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves estimated infrastructure geolocation results."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    locations = [ip.location for ip in enrichment.ip_intelligence]
    return {
        "email_id": email_id,
        "probable_origin_location": enrichment.probable_origin.location,
        "observed_locations": locations,
        "disclaimer": "Geolocation describes estimated infrastructure location, NOT the physical location or identity of the sender."
    }

@router.get("/{email_id}/domains", response_model=List[DomainIntelligenceSchema])
async def get_email_domain_intelligence(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves domain DNS records, registrar info, and domain registration age."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    return enrichment.domain_intelligence

@router.get("/{email_id}/reputation", response_model=List[ReputationIntelligenceSchema])
async def get_email_reputation(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves IP and domain reputation scores across intelligence providers."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    return enrichment.reputation

@router.get("/{email_id}/origin", response_model=ProbableOriginSchema)
async def get_email_probable_origin(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves calculated probable origin infrastructure and confidence calculation basis."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    return enrichment.probable_origin
