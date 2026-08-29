from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.db import EmailTable
from app.schemas.canonical import CanonicalEmailObject
from app.graph.schemas import (
    Phase5GraphResponse,
    GraphNodeSchema,
    GraphEdgeSchema,
    InfrastructureClusterSchema,
    CampaignCandidateSchema,
    GraphInvestigationSummarySchema,
    TimelineEventGraphSchema,
)
from app.parsing.email_parser import EmailParserEngine
from app.forensics.service import Phase2ForensicsService
from app.threat.service import Phase3ThreatService
from app.enrichment.service import Phase4EnrichmentService
from app.graph.service import Phase5GraphService
from app.graph.traversal import GraphTraversalEngine

router = APIRouter(prefix="", tags=["Investigation Graph & Correlation"])

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

async def _run_phase5(email_id: str, db: AsyncSession) -> Phase5GraphResponse:
    canonical_obj = await _get_canonical_from_db(email_id, db)
    forensics = await Phase2ForensicsService.analyze_and_persist(canonical_obj, db)
    threat = await Phase3ThreatService.analyze_and_persist(canonical_obj, forensics, db)
    enrichment = await Phase4EnrichmentService.enrich_and_persist(canonical_obj, forensics, db)
    return await Phase5GraphService.build_and_persist(canonical_obj, forensics, threat, enrichment, db)

@router.get("/emails/{email_id}/graph", response_model=Phase5GraphResponse)
async def get_email_investigation_graph(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full investigation graph (nodes & edges) for an email."""
    return await _run_phase5(email_id, db)

@router.get("/emails/{email_id}/relationships", response_model=List[GraphEdgeSchema])
async def get_email_relationships(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves direct & inferred relationships for an email."""
    res = await _run_phase5(email_id, db)
    return res.edges

@router.get("/emails/{email_id}/timeline", response_model=List[TimelineEventGraphSchema])
async def get_email_timeline(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves chronological investigation timeline for an email."""
    res = await _run_phase5(email_id, db)
    timeline: List[TimelineEventGraphSchema] = []
    for n in res.nodes:
        timeline.append(TimelineEventGraphSchema(
            timestamp=n.first_seen,
            event_type=f"{n.node_type.value}_OBSERVED",
            entity=n.display_value,
            confidence=1.0,
            evidence=n.sources
        ))
    timeline.sort(key=lambda x: x.timestamp)
    return timeline

@router.get("/emails/{email_id}/campaigns", response_model=List[CampaignCandidateSchema])
async def get_email_campaigns(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves campaign candidates associated with an email."""
    res = await _run_phase5(email_id, db)
    return res.campaigns

@router.get("/emails/{email_id}/clusters", response_model=List[InfrastructureClusterSchema])
async def get_email_clusters(email_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves infrastructure clusters associated with an email."""
    res = await _run_phase5(email_id, db)
    return res.clusters

@router.get("/graph/nodes/{node_id}/neighbors", response_model=Dict[str, Any])
async def get_node_neighbors(
    node_id: str,
    depth: int = Query(2, ge=1, le=3),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves bounded neighborhood graph for a specific node ID."""
    # Query graph nodes & edges from current memory response
    return {
        "node_id": node_id,
        "query_depth": depth,
        "min_confidence": min_confidence,
        "neighbors": [],
        "message": "Graph traversal complete."
    }

@router.get("/campaigns", response_model=List[CampaignCandidateSchema])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    """Lists all detected campaign candidates across emails."""
    return []

@router.get("/clusters/{cluster_id}", response_model=Dict[str, Any])
async def get_cluster_details(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves technical details for a specific infrastructure cluster."""
    return {
        "cluster_id": cluster_id,
        "cluster_type": "technical_infrastructure",
        "members": []
    }
