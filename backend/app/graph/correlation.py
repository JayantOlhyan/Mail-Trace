import uuid
from typing import List, Dict, Set
from app.graph.schemas import (
    GraphNodeSchema,
    GraphEdgeSchema,
    CampaignCandidateSchema,
)
from app.graph.taxonomy import NodeTypeEnum, CampaignStatusEnum
from app.graph.suppression import CommonInfrastructureSuppression

class CrossEmailCorrelationEngine:
    """
    Cross-Email Correlation Engine & Campaign Candidate Detector for ThreatTrace AI.
    Detects potential campaign candidates when multiple suspicious emails share
    meaningful technical infrastructure (IPs, Domains, URLs) within temporal windows.
    """

    @classmethod
    def detect_campaign_candidates(
        cls,
        nodes: List[GraphNodeSchema],
        edges: List[GraphEdgeSchema]
    ) -> List[CampaignCandidateSchema]:
        campaigns: List[CampaignCandidateSchema] = []

        # Find indicators connected to multiple emails
        email_nodes = [n for n in nodes if n.node_type == NodeTypeEnum.EMAIL]
        if len(email_nodes) < 2:
            return campaigns  # Campaign correlation requires at least 2 emails

        # Map non-email nodes to connected email IDs
        node_to_emails: Dict[str, Set[str]] = {}
        for edge in edges:
            src_node = next((n for n in nodes if n.node_id == edge.source_node), None)
            tgt_node = next((n for n in nodes if n.node_id == edge.target_node), None)

            if src_node and tgt_node:
                if src_node.node_type == NodeTypeEnum.EMAIL:
                    node_to_emails.setdefault(tgt_node.node_id, set()).add(src_node.canonical_value)
                elif tgt_node.node_type == NodeTypeEnum.EMAIL:
                    node_to_emails.setdefault(src_node.node_id, set()).add(tgt_node.canonical_value)

        # Identify shared indicators connected to 2+ emails
        for node_id, email_ids in node_to_emails.items():
            if len(email_ids) >= 2:
                target_node = next((n for n in nodes if n.node_id == node_id), None)
                if not target_node:
                    continue

                # Apply common infrastructure suppression
                suppression = CommonInfrastructureSuppression.get_suppression_penalty(
                    target_node.node_type.value, target_node.canonical_value, target_node.metadata
                )

                if suppression < 0.25:
                    continue  # Ignore shared common cloud/CDN infrastructure for campaign candidate grouping

                campaign_id = f"CMP-{uuid.uuid4().hex[:8]}"
                shared_infra = [target_node.canonical_value]
                shared_domains = [target_node.canonical_value] if target_node.node_type == NodeTypeEnum.DOMAIN else []

                explanation = (
                    f"Campaign candidate detected based on {len(email_ids)} emails sharing "
                    f"technical {target_node.node_type.value} indicator ({target_node.display_value})."
                )

                campaigns.append(CampaignCandidateSchema(
                    campaign_id=campaign_id,
                    status=CampaignStatusEnum.CANDIDATE,
                    confidence=round(0.82 * suppression, 2),
                    emails=list(email_ids),
                    shared_infrastructure=shared_infra,
                    shared_domains=shared_domains,
                    time_window={"start": target_node.first_seen, "end": target_node.last_seen},
                    explanation=explanation
                ))

        return campaigns
