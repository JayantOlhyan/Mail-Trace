from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.db import EmailTable
from app.schemas.canonical import CanonicalEmailObject, EvidenceRef, IdentitySchema, ContentSchema, HeadersSchema, IndicatorsSchema, MetadataSchema
from app.schemas.forensics import (
    Phase2ForensicAnalysisResponse,
    AuthenticationMatrixSchema,
    ForensicFindingSchema,
    TimelineEventSchema,
    RelayHopAnalysisSchema,
)
from app.forensics.service import Phase2ForensicsService
from app.ingestion.storage import EvidenceStorageHandler
from app.parsing.email_parser import EmailParserEngine

router = APIRouter(prefix="/emails", tags=["Forensics"])

async def _get_canonical_from_db(email_id: str, db: AsyncSession) -> CanonicalEmailObject:
    email_record = await db.get(EmailTable, email_id)
    if not email_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email ID {email_id} not found")

    # Read raw evidence bytes and re-parse canonical object cleanly
    evidence_path = email_record.evidence.storage_path
    with open(evidence_path, "rb") as f:
        raw_bytes = f.read()

    canonical_obj, _ = EmailParserEngine.parse_eml(raw_bytes, email_record.evidence_id, email_record.evidence.filename)
    return canonical_obj

@router.post("/{email_id}/forensics", response_model=Phase2ForensicAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_email_forensics(email_id: str, db: AsyncSession = Depends(get_db)):
    """Triggers or retrieves Phase 2 Email Forensics & Authentication Analysis."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    return await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)

@router.get("/{email_id}/forensics", response_model=Phase2ForensicAnalysisResponse)
async def get_email_forensics(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full Phase 2 forensic analysis JSON object."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    return await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)

@router.get("/{email_id}/authentication", response_model=AuthenticationMatrixSchema)
async def get_email_authentication(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves authentication matrix (SPF, DKIM, DMARC, ARC, Alignment)."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    analysis = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return analysis.authentication

@router.get("/{email_id}/findings", response_model=List[ForensicFindingSchema])
async def get_email_findings(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves list of structured forensic findings with evidence provenance & technical confidence."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    analysis = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return analysis.findings

@router.get("/{email_id}/timeline", response_model=List[TimelineEventSchema])
async def get_email_timeline(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves chronological forensic timeline events."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    analysis = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return analysis.timeline

@router.get("/{email_id}/trace", response_model=List[RelayHopAnalysisSchema])
async def get_email_trace(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves technical network relay hop chain."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    analysis = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return analysis.relay_analysis.hops
