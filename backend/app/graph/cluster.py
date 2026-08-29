import uuid
from typing import List, Dict
from app.graph.schemas import (
    GraphNodeSchema,
    GraphEdgeSchema,
    InfrastructureClusterSchema,
)
from app.graph.taxonomy import NodeTypeEnum
from app.graph.suppression import CommonInfrastructureSuppression

class InfrastructureClusteringEngine:
    """
    Groups related technical nodes (IP, Domain, Mail Server, URL) into shared infrastructure clusters.
    Applies common infrastructure suppression penalties to prevent false clustering.
    """

    @classmethod
    def identify_clusters(
        cls,
        nodes: List[GraphNodeSchema],
        edges: List[GraphEdgeSchema]
    ) -> List[InfrastructureClusterSchema]:
        clusters: List[InfrastructureClusterSchema] = []

        # Group technical nodes by IP address
        ip_nodes = [n for n in nodes if n.node_type == NodeTypeEnum.IP]

        for ip_node in ip_nodes:
            # Check suppression penalty
            suppression = CommonInfrastructureSuppression.get_suppression_penalty(
                "IP", ip_node.canonical_value, ip_node.metadata
            )
            if suppression < 0.30:
                continue  # Suppress common cloud infrastructure clusters

            cluster_id = f"INFRA-{uuid.uuid4().hex[:8]}"
            members = [ip_node.node_id]
            membership_scores = {ip_node.node_id: 1.0}

            # Find connected nodes (Domains, URLs)
            for edge in edges:
                if edge.source_node == ip_node.node_id or edge.target_node == ip_node.node_id:
                    other_id = edge.target_node if edge.source_node == ip_node.node_id else edge.source_node
                    other_node = next((n for n in nodes if n.node_id == other_id), None)
                    if other_node and other_node.node_type in (NodeTypeEnum.DOMAIN, NodeTypeEnum.URL, NodeTypeEnum.MAIL_SERVER):
                        if other_id not in members:
                            members.append(other_id)
                            membership_scores[other_id] = round(edge.confidence * suppression, 2)

            if len(members) >= 2:
                clusters.append(InfrastructureClusterSchema(
                    cluster_id=cluster_id,
                    cluster_key=f"infra_{ip_node.canonical_value.replace('.', '_')}",
                    cluster_type="technical_infrastructure",
                    confidence=round(0.85 * suppression, 2),
                    members=members,
                    membership_scores=membership_scores
                ))

        return clusters
