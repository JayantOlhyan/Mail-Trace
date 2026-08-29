from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.schemas.threat import Phase3ThreatAnalysisResponse
from app.enrichment.schemas import Phase4EnrichmentResponse
from app.graph.schemas import (
    Phase5GraphResponse,
    GraphNodeSchema,
    GraphEdgeSchema,
    InfrastructureClusterSchema,
    CampaignCandidateSchema,
)
from app.graph.builder import GraphBuilder
from app.graph.cluster import InfrastructureClusteringEngine
from app.graph.correlation import CrossEmailCorrelationEngine
from app.models.db import (
    EmailTable,
    GraphNodeTable,
    GraphNodeSourceTable,
    GraphEdgeTable,
    GraphEdgeEvidenceTable,
    InfrastructureClusterTable,
    ClusterMemberTable,
    CampaignTable,
    CampaignMemberTable,
)

class Phase5GraphService:
    """
    Phase 5 Master Orchestrator for Infrastructure Correlation, Investigation Graph & Campaign Analysis.
    Builds canonical evidence-backed nodes & edges -> Performs entity resolution -> Calculates clusters ->
    Detects campaign candidates -> Persists to database idempotently.
    """

    @classmethod
    async def build_and_persist(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        threat: Phase3ThreatAnalysisResponse,
        enrichment: Phase4EnrichmentResponse,
        db: AsyncSession
    ) -> Phase5GraphResponse:
        email_id = canonical_email.email_id

        # 1. Build local graph for this email
        nodes, edges = GraphBuilder.build_graph_for_email(canonical_email, forensics, threat, enrichment)

        # 2. Entity Resolution: Fetch existing global nodes to merge duplicate entities
        stmt_n = select(GraphNodeTable)
        existing_db_nodes = (await db.execute(stmt_n)).scalars().all()
        existing_node_map = {n.canonical_value: n for n in existing_db_nodes}

        # Resolve & merge duplicate nodes
        resolved_nodes: List[GraphNodeSchema] = []
        node_id_remap: Dict[str, str] = {}

        for n in nodes:
            if n.canonical_value in existing_node_map:
                existing_n = existing_node_map[n.canonical_value]
                node_id_remap[n.node_id] = existing_n.id

                # Merge sources
                all_sources = list(set(existing_n.sources + n.sources))
                resolved_nodes.append(GraphNodeSchema(
                    node_id=existing_n.id,
                    node_type=n.node_type,
                    canonical_value=n.canonical_value,
                    display_value=n.display_value,
                    first_seen=existing_n.first_seen,
                    last_seen=datetime.utcnow().isoformat(),
                    metadata={**n.metadata},
                    sources=all_sources
                ))
            else:
                resolved_nodes.append(n)

        # Remap edge source/target IDs
        resolved_edges: List[GraphEdgeSchema] = []
        for e in edges:
            src = node_id_remap.get(e.source_node, e.source_node)
            tgt = node_id_remap.get(e.target_node, e.target_node)
            resolved_edges.append(GraphEdgeSchema(
                edge_id=e.edge_id,
                source_node=src,
                target_node=tgt,
                relationship=e.relationship,
                relationship_type=e.relationship_type,
                confidence=e.confidence,
                strength=e.strength,
                evidence=e.evidence,
                first_observed=e.first_observed,
                last_observed=e.last_observed,
                metadata=e.metadata
            ))

        # 3. Identify Infrastructure Clusters
        clusters = InfrastructureClusteringEngine.identify_clusters(resolved_nodes, resolved_edges)

        # 4. Detect Campaign Candidates
        campaigns = CrossEmailCorrelationEngine.detect_campaign_candidates(resolved_nodes, resolved_edges)

        response = Phase5GraphResponse(
            nodes=resolved_nodes,
            edges=resolved_edges,
            clusters=clusters,
            campaigns=campaigns
        )

        # 5. Idempotent Persistence
        await cls._persist_to_db(email_id, response, db)

        return response

    @classmethod
    async def _persist_to_db(cls, email_id: str, response: Phase5GraphResponse, db: AsyncSession) -> None:
        email_record = await db.get(EmailTable, email_id)
        if not email_record:
            return

        # Persist Nodes
        for n in response.nodes:
            db_n = await db.get(GraphNodeTable, n.node_id)
            if not db_n:
                db_n = GraphNodeTable(
                    id=n.node_id,
                    node_type=n.node_type.value,
                    canonical_value=n.canonical_value,
                    display_value=n.display_value,
                    first_seen=n.first_seen,
                    last_seen=n.last_seen
                )
                db.add(db_n)
            else:
                db_n.last_seen = n.last_seen

            await db.flush()
            # Add source email linkage
            db.add(GraphNodeSourceTable(
                node_id=n.node_id,
                email_id=email_id,
                source_reference=f"email_{email_id}"
            ))

        # Persist Edges
        for e in response.edges:
            db_e = await db.get(GraphEdgeTable, e.edge_id)
            if not db_e:
                db_e = GraphEdgeTable(
                    id=e.edge_id,
                    source_node_id=e.source_node,
                    target_node_id=e.target_node,
                    relationship_type=e.relationship.value,
                    relationship_origin=e.relationship_type.value,
                    confidence=e.confidence,
                    strength=e.strength.value,
                    first_observed=e.first_observed,
                    last_observed=e.last_observed
                )
                db.add(db_e)
                await db.flush()

                for ev in e.evidence:
                    db.add(GraphEdgeEvidenceTable(
                        edge_id=e.edge_id,
                        source_phase=ev.source_phase,
                        source_type=ev.source_type,
                        evidence_reference=ev.evidence_reference,
                        provider=ev.provider,
                        observed_at=ev.observed_at
                    ))

        # Persist Clusters
        for c in response.clusters:
            db_c = await db.get(InfrastructureClusterTable, c.cluster_id)
            if not db_c:
                db_c = InfrastructureClusterTable(
                    id=c.cluster_id,
                    cluster_key=c.cluster_key,
                    cluster_type=c.cluster_type,
                    confidence=c.confidence,
                    first_seen=c.first_seen,
                    last_seen=c.last_seen
                )
                db.add(db_c)
                await db.flush()

                for m_id, m_score in c.membership_scores.items():
                    db.add(ClusterMemberTable(
                        cluster_id=c.cluster_id,
                        node_id=m_id,
                        membership_score=m_score
                    ))

        # Persist Campaigns
        for cmp in response.campaigns:
            db_cmp = await db.get(CampaignTable, cmp.campaign_id)
            if not db_cmp:
                db_cmp = CampaignTable(
                    id=cmp.campaign_id,
                    campaign_id=cmp.campaign_id,
                    confidence=cmp.confidence,
                    status=cmp.status.value,
                    summary=cmp.explanation,
                    first_seen=cmp.time_window.get("start", datetime.utcnow().isoformat()),
                    last_seen=cmp.time_window.get("end", datetime.utcnow().isoformat())
                )
                db.add(db_cmp)
                await db.flush()

                for m_email in cmp.emails:
                    db.add(CampaignMemberTable(
                        campaign_id=cmp.campaign_id,
                        email_id=m_email,
                        membership_score=0.90
                    ))

        await db.commit()
