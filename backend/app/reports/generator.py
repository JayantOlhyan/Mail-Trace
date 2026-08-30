from datetime import datetime
from typing import Dict, List, Any, Optional

from app.schemas.reports import (
    ForensicReportSchema,
    MachineFindingsSchema,
    AnalystFindingsSchema,
    ThreatFindingReportSchema,
    EvidenceItemSchema,
    ChainOfCustodyItemSchema,
)
from app.reports.hashing import create_evidence_item, calculate_sha256


class ForensicReportGenerator:
    """
    Master Forensic Report Builder for MailTrace (Phase 7).
    Consumes outputs from Phases 1-6 and produces structured ForensicReportSchema.
    """

    def generate_report(
        self,
        case_id: str,
        investigation_id: str,
        email_data: Dict[str, Any],
        threat_assessment: Dict[str, Any],
        header_forensics: Dict[str, Any],
        infrastructure_data: Dict[str, Any],
        graph_data: Dict[str, Any],
        analyst_notes: List[Dict[str, Any]] = None,
        analyst_decision: Optional[str] = None,
        case_status: str = "OPEN",
        assigned_analyst: str = "Analyst",
        campaign_data: Optional[Dict[str, Any]] = None,
        version: str = "1.0",
    ) -> ForensicReportSchema:

        if case_id.startswith("CASE-"):
            report_id = case_id.replace("CASE-", "RPT-")
        else:
            report_id = f"RPT-{case_id}"
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S IST")

        # 1. Build Evidence Inventory with SHA-256 Hashes
        evidence_inventory: List[EvidenceItemSchema] = [
            create_evidence_item(
                evidence_id=f"EVD-{case_id}-01",
                evidence_type="Raw Email Payload",
                source="Email Ingestion Engine",
                origin_phase="Phase 1",
                raw_content=email_data,
                case_id=case_id,
            ),
            create_evidence_item(
                evidence_id=f"EVD-{case_id}-02",
                evidence_type="Header Authentication Analysis",
                source="Forensic Header Parser",
                origin_phase="Phase 2",
                raw_content=header_forensics,
                case_id=case_id,
            ),
            create_evidence_item(
                evidence_id=f"EVD-{case_id}-03",
                evidence_type="AI Threat Assessment",
                source="Threat Detection Engine",
                origin_phase="Phase 3",
                raw_content=threat_assessment,
                case_id=case_id,
            ),
            create_evidence_item(
                evidence_id=f"EVD-{case_id}-04",
                evidence_type="Infrastructure & Geolocation Intelligence",
                source="Enrichment Service",
                origin_phase="Phase 4",
                raw_content=infrastructure_data,
                case_id=case_id,
            ),
        ]

        # 2. Build Chain of Custody History
        chain_of_custody: List[ChainOfCustodyItemSchema] = [
            ChainOfCustodyItemSchema(
                id=1,
                evidence_id=f"EVD-{case_id}-01",
                action="Captured & Normalized",
                timestamp=email_data.get("received_at", generated_at),
                actor="MailTrace Ingestion Pipeline",
                details="Cryptographic hash computed and evidence stored passively.",
            ),
            ChainOfCustodyItemSchema(
                id=2,
                evidence_id=f"EVD-{case_id}-02",
                action="Header Forensics & Authentication Verification",
                timestamp=generated_at,
                actor="Phase 2 Evaluator Engine",
                details="Evaluated SPF, DKIM, DMARC alignment and hop chain.",
            ),
            ChainOfCustodyItemSchema(
                id=3,
                evidence_id=f"EVD-{case_id}-03",
                action="AI Threat Assessment & Risk Scoring",
                timestamp=generated_at,
                actor="Phase 3 Multi-Signal Engine",
                details=f"Assigned risk score {threat_assessment.get('risk_score', 0)}/100.",
            ),
            ChainOfCustodyItemSchema(
                id=4,
                evidence_id=f"EVD-{case_id}-04",
                action="Added to Incident Case",
                timestamp=generated_at,
                actor=assigned_analyst,
                details=f"Associated with case {case_id} for investigative reporting.",
            ),
        ]

        # 3. Machine vs Analyst Separation
        machine_findings = MachineFindingsSchema(
            ai_classification=threat_assessment.get("classification", "SUSPICIOUS"),
            risk_score=threat_assessment.get("risk_score", 0),
            confidence=threat_assessment.get("confidence", "HIGH"),
            spf_status=header_forensics.get("spf_status", "UNKNOWN"),
            dkim_status=header_forensics.get("dkim_status", "UNKNOWN"),
            dmarc_status=header_forensics.get("dmarc_status", "UNKNOWN"),
            detected_indicators=[
                f["finding"] for f in threat_assessment.get("findings", [])
            ],
            origin_ip=infrastructure_data.get("ip"),
            origin_asn=infrastructure_data.get("asn"),
            origin_location=infrastructure_data.get("location"),
            infrastructure_clusters=[
                infrastructure_data.get("cluster_id")
            ] if infrastructure_data.get("cluster_id") else [],
            campaign_candidates=[
                campaign_data.get("campaign_id")
            ] if campaign_data and campaign_data.get("campaign_id") else [],
        )

        analyst_findings = AnalystFindingsSchema(
            analyst_classification=analyst_decision,
            analyst_confidence="HIGH" if analyst_decision else None,
            case_status=case_status,
            assigned_analyst=assigned_analyst,
            analyst_notes=analyst_notes or [],
            analyst_decision=analyst_decision or "ANALYST CONCLUSION PENDING",
            recommended_actions=[
                "Block identified deceptive domains and relay IPs on perimeter firewalls.",
                "Revoke compromise-suspected user sessions and enforce MFA reset.",
                "Correlate shared infrastructure indicators across SIEM/SOAR logs.",
                "Preserve cryptographic evidence package for regulatory reporting.",
            ],
        )

        # 4. Threat Findings Conversion
        threat_findings = [
            ThreatFindingReportSchema(
                id=f.get("id", f"FND-00{idx+1}"),
                finding=f.get("finding", ""),
                category=f.get("category", "General Security"),
                severity=f.get("severity", "MEDIUM"),
                evidence_reference=f.get("evidence_reference", "Header Evaluation"),
                originating_phase=f.get("originating_phase", "Phase 3"),
            )
            for idx, f in enumerate(threat_assessment.get("findings", []))
        ]

        # 5. Executive Summary Generation
        exec_summary = (
            f"MailTrace evaluated email object '{investigation_id}' and identified a "
            f"{threat_assessment.get('classification', 'SUSPICIOUS')} event with a defensive risk score of "
            f"{threat_assessment.get('risk_score', 0)}/100 ({threat_assessment.get('confidence', 'HIGH')} confidence). "
            f"Key triggers include authentication failures and suspicious origin infrastructure in "
            f"{infrastructure_data.get('location', 'observed network')}."
        )

        # 6. Extract IOCs
        iocs = [
            {
                "ioc": email_data.get("sender"),
                "type": "Email / Sender",
                "confidence": "HIGH",
                "source": "From: Header",
            },
            {
                "ioc": email_data.get("sender_domain"),
                "type": "Domain",
                "confidence": "HIGH",
                "source": "Domain Parser",
            },
        ]
        if infrastructure_data.get("ip"):
            iocs.append({
                "ioc": infrastructure_data.get("ip"),
                "type": "IP Address",
                "confidence": "HIGH",
                "source": "Origin Relay Tracing",
            })

        return ForensicReportSchema(
            report_id=report_id,
            case_id=case_id,
            version=version,
            generated_at=generated_at,
            generated_by="MailTrace Forensic Engine v1.0",
            investigation_id=investigation_id,
            evidence_count=len(evidence_inventory),
            executive_summary=exec_summary,
            machine_findings=machine_findings,
            analyst_findings=analyst_findings,
            threat_findings=threat_findings,
            email_metadata=email_data,
            header_forensics=header_forensics,
            relay_path=header_forensics.get("received_hops", []),
            infrastructure_intelligence=infrastructure_data,
            indicators_of_compromise=iocs,
            graph_summary={
                "nodes_count": len(graph_data.get("nodes", [])),
                "edges_count": len(graph_data.get("edges", [])),
                "nodes": graph_data.get("nodes", []),
            },
            campaign_analysis=campaign_data,
            timeline_events=[
                {
                    "timestamp": email_data.get("received_at", generated_at),
                    "title": "Email Ingestion & Threat Detection",
                    "description": f"Analyzed email {investigation_id} (Score: {threat_assessment.get('risk_score', 0)}/100)",
                }
            ],
            evidence_inventory=evidence_inventory,
            chain_of_custody=chain_of_custody,
        )
