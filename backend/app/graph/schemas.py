from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.graph.taxonomy import (
    NodeTypeEnum,
    EdgeRelationshipEnum,
    RelationshipOriginEnum,
    RelationshipStrengthEnum,
    CampaignStatusEnum,
)

class EdgeEvidenceSchema(BaseModel):
    source_phase: str = Field(..., description="Phase 1, Phase 2, Phase 3, or Phase 4")
    source_type: str = Field(..., description="Evidence source type (received_header, dns, etc.)")
    evidence_reference: str = Field(..., description="Reference ID or rule code")
    provider: Optional[str] = Field(None, description="Provider name if applicable")
    observed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class GraphNodeSchema(BaseModel):
    node_id: str = Field(..., description="Unique node ID (e.g. NODE-IP-xxxxxx)")
    node_type: NodeTypeEnum = Field(..., description="Node taxonomy type")
    canonical_value: str = Field(..., description="Normalized canonical value")
    display_value: str = Field(..., description="Display label")
    first_seen: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list, description="Source email IDs or reference IDs")

class GraphEdgeSchema(BaseModel):
    edge_id: str = Field(..., description="Unique edge ID (e.g. EDGE-xxxxxx)")
    source_node: str = Field(..., description="Source node ID")
    target_node: str = Field(..., description="Target node ID")
    relationship: EdgeRelationshipEnum = Field(..., description="Edge relationship type")
    relationship_type: RelationshipOriginEnum = Field(RelationshipOriginEnum.DIRECT, description="DIRECT or INFERRED")
    confidence: float = Field(..., description="Relationship confidence score (0.0 to 1.0)")
    strength: RelationshipStrengthEnum = Field(..., description="VERY_HIGH, HIGH, MEDIUM, LOW, VERY_LOW")
    evidence: List[EdgeEvidenceSchema] = Field(default_factory=list)
    first_observed: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_observed: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InfrastructureClusterSchema(BaseModel):
    cluster_id: str = Field(..., description="Unique cluster ID (INFRA-xxxxxx)")
    cluster_key: str = Field(..., description="Cluster identifier key")
    cluster_type: str = Field("technical_infrastructure", description="Cluster category")
    confidence: float = Field(..., description="Cluster confidence score (0.0 to 1.0)")
    members: List[str] = Field(default_factory=list, description="Node IDs of member entities")
    membership_scores: Dict[str, float] = Field(default_factory=dict, description="Node ID to membership score mapping")
    first_seen: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CampaignCandidateSchema(BaseModel):
    campaign_id: str = Field(..., description="Unique campaign ID (CMP-xxxxxx)")
    status: CampaignStatusEnum = Field(CampaignStatusEnum.CANDIDATE, description="CANDIDATE, UNDER_REVIEW, etc.")
    confidence: float = Field(..., description="Campaign candidate confidence score (0.0 to 1.0)")
    emails: List[str] = Field(default_factory=list, description="Email IDs included in campaign candidate")
    shared_infrastructure: List[str] = Field(default_factory=list, description="Shared IP/Domain/URL values")
    shared_domains: List[str] = Field(default_factory=list)
    time_window: Dict[str, str] = Field(default_factory=dict, description="start and end timestamps")
    explanation: str = Field("", description="Evidence-backed explanation for campaign grouping")
    limitations: List[str] = Field(default_factory=lambda: [
        "Campaign candidate relationships are machine-generated indicators and require analyst confirmation.",
        "Shared cloud infrastructure alone is not proof of common authorship."
    ])

class TimelineEventGraphSchema(BaseModel):
    timestamp: str = Field(..., description="ISO timestamp")
    event_type: str = Field(..., description="DOMAIN_REGISTERED, EMAIL_OBSERVED, DNS_RESOLVED, etc.")
    entity: str = Field(..., description="Associated node ID or indicator value")
    confidence: float = Field(1.0, description="Event observation confidence")
    evidence: List[str] = Field(default_factory=list)

class GraphInvestigationSummarySchema(BaseModel):
    email_id: str = Field(..., description="Target email ID")
    direct_connections: int = Field(0, description="Number of direct node connections")
    related_emails: int = Field(0, description="Number of correlated emails")
    infrastructure_clusters: int = Field(0, description="Number of associated infrastructure clusters")
    campaign_candidates: int = Field(0, description="Number of associated campaign candidates")
    strongest_relationships: List[GraphEdgeSchema] = Field(default_factory=list)
    key_indicators: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=lambda: [
        "Correlation does NOT establish attacker identity or physical location.",
        "Infrastructure ownership does not prove common authorship."
    ])

class Phase5GraphResponse(BaseModel):
    nodes: List[GraphNodeSchema] = Field(default_factory=list)
    edges: List[GraphEdgeSchema] = Field(default_factory=list)
    clusters: List[InfrastructureClusterSchema] = Field(default_factory=list)
    campaigns: List[CampaignCandidateSchema] = Field(default_factory=list)
