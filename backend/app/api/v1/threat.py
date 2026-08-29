from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.db import EmailTable
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.threat import (
    Phase3ThreatAnalysisResponse,
    ThreatSignalSchema,
    ThreatRiskAssessmentSchema,
    ThreatEvidenceSpanSchema,
)
from app.parsing.email_parser import EmailParserEngine
from app.forensics.service import Phase2ForensicsService
from app.threat.service import Phase3ThreatService

router = APIRouter(prefix="/emails", tags=["Threat Detection"])

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

@router.post("/{email_id}/threat-analysis", response_model=Phase3ThreatAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_email_threat(email_id: str, db: AsyncSession = Depends(get_db)):
    """Triggers or retrieves Phase 3 AI Threat Detection & Risk Assessment Engine analysis."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)

@router.get("/{email_id}/threat-analysis", response_model=Phase3ThreatAnalysisResponse)
async def get_email_threat_analysis(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full Phase 3 threat analysis JSON object."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    return await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)

@router.get("/{email_id}/threat-signals", response_model=List[ThreatSignalSchema])
async def get_email_threat_signals(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves list of extracted threat signals."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    analysis = await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    return analysis.signals

@router.get("/{email_id}/risk", response_model=ThreatRiskAssessmentSchema)
async def get_email_risk_assessment(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves 0-100 risk score and risk level assessment."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    analysis = await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    return analysis.risk

@router.get("/{email_id}/explanation", response_model=Dict[str, Any])
async def get_email_explanation(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves explainable threat summary grounded in evidence text spans."""
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    analysis = await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    return {
        "email_id": email_id,
        "primary_classification": analysis.classification.primary.value,
        "risk_level": analysis.risk.level.value,
        "risk_score": analysis.risk.score,
        "explanation": analysis.explanation,
        "evidence_spans": analysis.evidence
    }
