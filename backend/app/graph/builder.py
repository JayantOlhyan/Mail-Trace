import uuid
from typing import List, Dict, Tuple, Any
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.schemas.threat import Phase3ThreatAnalysisResponse
from app.enrichment.schemas import Phase4EnrichmentResponse
from app.graph.schemas import (
    GraphNodeSchema,
    GraphEdgeSchema,
    EdgeEvidenceSchema,
)
from app.graph.taxonomy import (
    NodeTypeEnum,
    EdgeRelationshipEnum,
    RelationshipOriginEnum,
    RelationshipStrengthEnum,
)
from app.graph.normalizer import EntityNormalizer

class GraphBuilder:
    """
    Extracts evidence-backed nodes and edges from Phase 1, Phase 2, Phase 3, and Phase 4 data models.
    """

    @classmethod
    def build_graph_for_email(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        threat: Phase3ThreatAnalysisResponse,
        enrichment: Phase4EnrichmentResponse
    ) -> Tuple[List[GraphNodeSchema], List[GraphEdgeSchema]]:
        nodes_map: Dict[str, GraphNodeSchema] = {}
        edges: List[GraphEdgeSchema] = []

        email_id = canonical_email.email_id
        email_node_id = f"NODE-EMAIL-{email_id}"

        # 1. Root EMAIL Node
        email_node = GraphNodeSchema(
            node_id=email_node_id,
            node_type=NodeTypeEnum.EMAIL,
            canonical_value=email_id,
            display_value=f"Email ({email_id[:10]})",
            sources=[email_id],
            metadata={
                "subject": canonical_email.content.subject,
                "threat_primary": threat.classification.primary.value,
                "risk_score": threat.risk.score
            }
        )
        nodes_map[email_node_id] = email_node

        # 2. SENDER Node (SENT_BY edge)
        if canonical_email.identity.from_:
            sender_addr = canonical_email.identity.from_[0].address
            clean_s, disp_s = EntityNormalizer.normalize_email_address(sender_addr)
            sender_node_id = f"NODE-SENDER-{clean_s}"

            if sender_node_id not in nodes_map:
                nodes_map[sender_node_id] = GraphNodeSchema(
                    node_id=sender_node_id,
                    node_type=NodeTypeEnum.SENDER,
                    canonical_value=clean_s,
                    display_value=disp_s,
                    sources=[email_id]
                )

            edges.append(GraphEdgeSchema(
                edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source_node=email_node_id,
                target_node=sender_node_id,
                relationship=EdgeRelationshipEnum.SENT_BY,
                relationship_type=RelationshipOriginEnum.DIRECT,
                confidence=0.98,
                strength=RelationshipStrengthEnum.VERY_HIGH,
                evidence=[EdgeEvidenceSchema(
                    source_phase="PHASE_1",
                    source_type="from_header",
                    evidence_reference=f"From: {disp_s}"
                )]
            ))

        # 3. DOMAIN Nodes (SIGNED_BY edge for DKIM)
        if forensics.authentication.dkim.signing_domain:
            clean_d, disp_d = EntityNormalizer.normalize_domain(forensics.authentication.dkim.signing_domain)
            dom_node_id = f"NODE-DOMAIN-{clean_d}"

            if dom_node_id not in nodes_map:
                nodes_map[dom_node_id] = GraphNodeSchema(
                    node_id=dom_node_id,
                    node_type=NodeTypeEnum.DOMAIN,
                    canonical_value=clean_d,
                    display_value=disp_d,
                    sources=[email_id]
                )

            edges.append(GraphEdgeSchema(
                edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source_node=email_node_id,
                target_node=dom_node_id,
                relationship=EdgeRelationshipEnum.SIGNED_BY,
                relationship_type=RelationshipOriginEnum.DIRECT,
                confidence=0.95,
                strength=RelationshipStrengthEnum.HIGH,
                evidence=[EdgeEvidenceSchema(
                    source_phase="PHASE_2",
                    source_type="dkim_header",
                    evidence_reference=f"d={clean_d}"
                )]
            ))

        # 4. IP Nodes (PASSED_THROUGH edges from Relay chain)
        for hop in forensics.relay_analysis.hops:
            if hop.source_ip:
                clean_ip, disp_ip = EntityNormalizer.normalize_ip(hop.source_ip)
                ip_node_id = f"NODE-IP-{clean_ip}"

                if ip_node_id not in nodes_map:
                    nodes_map[ip_node_id] = GraphNodeSchema(
                        node_id=ip_node_id,
                        node_type=NodeTypeEnum.IP,
                        canonical_value=clean_ip,
                        display_value=disp_ip,
                        sources=[email_id]
                    )

                edges.append(GraphEdgeSchema(
                    edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                    source_node=email_node_id,
                    target_node=ip_node_id,
                    relationship=EdgeRelationshipEnum.PASSED_THROUGH,
                    relationship_type=RelationshipOriginEnum.DIRECT,
                    confidence=0.96,
                    strength=RelationshipStrengthEnum.VERY_HIGH,
                    evidence=[EdgeEvidenceSchema(
                        source_phase="PHASE_2",
                        source_type="received_header",
                        evidence_reference=f"hop_{hop.hop}"
                    )]
                ))

        # 5. IP Enrichment Connections (BELONGS_TO_ASN, GEOLOCATED_TO edges from Phase 4)
        for ip_intel in enrichment.ip_intelligence:
            clean_ip, _ = EntityNormalizer.normalize_ip(ip_intel.ip)
            ip_node_id = f"NODE-IP-{clean_ip}"

            if ip_intel.network.asn:
                asn_clean = ip_intel.network.asn.upper()
                asn_node_id = f"NODE-ASN-{asn_clean}"
                if asn_node_id not in nodes_map:
                    nodes_map[asn_node_id] = GraphNodeSchema(
                        node_id=asn_node_id,
                        node_type=NodeTypeEnum.ASN,
                        canonical_value=asn_clean,
                        display_value=f"{asn_clean} ({ip_intel.network.organization or ''})",
                        sources=[email_id],
                        metadata={"organization": ip_intel.network.organization, "isp": ip_intel.network.isp}
                    )

                edges.append(GraphEdgeSchema(
                    edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                    source_node=ip_node_id,
                    target_node=asn_node_id,
                    relationship=EdgeRelationshipEnum.BELONGS_TO_ASN,
                    relationship_type=RelationshipOriginEnum.DIRECT,
                    confidence=0.90,
                    strength=RelationshipStrengthEnum.HIGH,
                    evidence=[EdgeEvidenceSchema(
                        source_phase="PHASE_4",
                        source_type="asn_lookup",
                        evidence_reference=asn_clean,
                        provider=ip_intel.location.provider
                    )]
                ))

            if ip_intel.location.country:
                loc_name = f"{ip_intel.location.city or ''}, {ip_intel.location.country}".strip(", ")
                loc_node_id = f"NODE-LOCATION-{loc_name.lower().replace(' ', '_')}"
                if loc_node_id not in nodes_map:
                    nodes_map[loc_node_id] = GraphNodeSchema(
                        node_id=loc_node_id,
                        node_type=NodeTypeEnum.LOCATION,
                        canonical_value=loc_name,
                        display_value=loc_name,
                        sources=[email_id]
                    )

                edges.append(GraphEdgeSchema(
                    edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                    source_node=ip_node_id,
                    target_node=loc_node_id,
                    relationship=EdgeRelationshipEnum.GEOLOCATED_TO,
                    relationship_type=RelationshipOriginEnum.INFERRED,
                    confidence=ip_intel.location.confidence,
                    strength=RelationshipStrengthEnum.MEDIUM,
                    evidence=[EdgeEvidenceSchema(
                        source_phase="PHASE_4",
                        source_type="geoip_lookup",
                        evidence_reference=loc_name,
                        provider=ip_intel.location.provider
                    )]
                ))

        # 6. URL Nodes (CONTAINS_URL edges)
        for u in canonical_email.indicators.urls:
            clean_url, disp_url = EntityNormalizer.normalize_url(u.raw_url)
            url_node_id = f"NODE-URL-{uuid.uuid4().hex[:8]}"

            nodes_map[url_node_id] = GraphNodeSchema(
                node_id=url_node_id,
                node_type=NodeTypeEnum.URL,
                canonical_value=clean_url,
                display_value=disp_url,
                sources=[email_id]
            )

            edges.append(GraphEdgeSchema(
                edge_id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source_node=email_node_id,
                target_node=url_node_id,
                relationship=EdgeRelationshipEnum.CONTAINS_URL,
                relationship_type=RelationshipOriginEnum.DIRECT,
                confidence=0.99,
                strength=RelationshipStrengthEnum.VERY_HIGH,
                evidence=[EdgeEvidenceSchema(
                    source_phase="PHASE_1",
                    source_type="email_body_url",
                    evidence_reference=disp_url[:40]
                )]
            ))

        return list(nodes_map.values()), edges
