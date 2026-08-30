from typing import Dict, List, Any
from app.reports.generator import ForensicReportGenerator


class SIHDemoEnvironment:
    """
    Controlled SIH 2026 Demonstration Mode Provider & Dataset Handler.
    Provides realistic evaluation cases including legitimate emails.
    """

    def __init__(self):
        self.reset_demo_data()

    def reset_demo_data(self):
        """
        Restores SIH Demo dataset to baseline state.
        """
        self.demo_emails = {
            "EML-2026-8801": {
                "id": "EML-2026-8801",
                "subject": "URGENT: Payroll Verification & Direct Deposit Update Required",
                "sender": "payroll-update@paypa1-support.com",
                "sender_domain": "paypa1-support.com",
                "received_at": "2026-08-30T14:23:10Z",
                "risk_score": 91,
                "classification": "PHISHING",
                "status": "UNDER_INVESTIGATION",
                "message_id": "<202608301423.8801@paypa1-support.com>",
            },
            "EML-2026-8802": {
                "id": "EML-2026-8802",
                "subject": "Wire Transfer Authorization for Q3 Vendor Invoice #8849",
                "sender": "ceo-office@exec-management-corp.net",
                "sender_domain": "exec-management-corp.net",
                "received_at": "2026-08-30T12:10:00Z",
                "risk_score": 87,
                "classification": "BEC",
                "status": "OPEN",
                "message_id": "<202608301210.8802@exec-management-corp.net>",
            },
            "EML-2026-8803": {
                "id": "EML-2026-8803",
                "subject": "Security Alert: Password Reset Required Immediately",
                "sender": "security@auth-services-portal.org",
                "sender_domain": "auth-services-portal.org",
                "received_at": "2026-08-29T18:45:22Z",
                "risk_score": 78,
                "classification": "IMPERSONATION",
                "status": "ESCALATED",
                "message_id": "<202608291845.8803@auth-services-portal.org>",
            },
            "EML-2026-8804": {
                "id": "EML-2026-8804",
                "subject": "Quarterly Team All-Hands Agenda & Slide Deck",
                "sender": "hr@legitimate-company.com",
                "sender_domain": "legitimate-company.com",
                "received_at": "2026-08-29T10:15:00Z",
                "risk_score": 8,
                "classification": "LEGITIMATE",
                "status": "CLOSED",
                "message_id": "<202608291015.8804@legitimate-company.com>",
            },
        }

        self.demo_cases = {
            "CASE-2026-0042": {
                "case_id": "CASE-2026-0042",
                "title": "High-Risk Financial Credential Harvesting Campaign",
                "priority": "HIGH",
                "status": "OPEN",
                "assigned_to": "Senior Analyst Jayant",
                "email_id": "EML-2026-8801",
            }
        }

    def get_demo_report(self, case_id: str = "CASE-2026-0042"):
        """
        Builds a complete forensic report for SIH judging demonstration.
        """
        case_info = self.demo_cases.get(case_id, self.demo_cases["CASE-2026-0042"])
        email_data = self.demo_emails[case_info["email_id"]]

        threat_assessment = {
            "risk_score": email_data["risk_score"],
            "classification": email_data["classification"],
            "confidence": "HIGH",
            "findings": [
                {
                    "id": "FND-001",
                    "finding": "Domain paypa1-support.com is a deceptive lookalike of paypal.com.",
                    "category": "Lookalike Domain",
                    "severity": "HIGH",
                    "evidence_reference": "RFC5322 From: header",
                    "originating_phase": "Phase 3",
                },
                {
                    "id": "FND-002",
                    "finding": "SPF verification failed (softfail) for IP 203.0.113.10.",
                    "category": "Authentication Failure",
                    "severity": "HIGH",
                    "evidence_reference": "Received SPF line 2",
                    "originating_phase": "Phase 2",
                },
            ],
        }

        header_forensics = {
            "spf_status": "FAIL",
            "dkim_status": "FAIL",
            "dmarc_status": "FAIL",
            "from_address": email_data["sender"],
            "reply_to": "harvest-collector@random-drop-domain.com",
            "message_id": email_data["message_id"],
            "received_hops": [
                {
                    "hop_index": 1,
                    "from_server": "mail.paypa1-support.com",
                    "by_server": "mta-01.relay-host.net",
                    "ip": "203.0.113.10",
                    "timestamp": "2026-08-30T14:22:58Z",
                    "is_suspicious": True,
                }
            ],
        }

        infrastructure_data = {
            "ip": "203.0.113.10",
            "asn": "AS12345",
            "organization": "Bulletproof Hosting Ltd",
            "location": "Frankfurt, Germany",
            "cluster_id": "INFRA-004",
        }

        graph_data = {
            "nodes": [
                {"id": "NODE-EML", "node_type": "EMAIL", "canonical_value": email_data["id"]},
                {"id": "NODE-IP", "node_type": "IP", "canonical_value": "203.0.113.10"},
                {"id": "NODE-ASN", "node_type": "ASN", "canonical_value": "AS12345"},
            ],
            "edges": [
                {"id": "EDGE-1", "source_node_id": "NODE-EML", "target_node_id": "NODE-IP", "relationship_type": "PASSED_THROUGH"},
                {"id": "EDGE-2", "source_node_id": "NODE-IP", "target_node_id": "NODE-ASN", "relationship_type": "BELONGS_TO_ASN"},
            ],
        }

        campaign_data = {
            "campaign_id": "CMP-2026-001",
            "confidence": 88,
            "status": "CANDIDATE",
            "summary": "Targeted Financial Phishing Campaign",
        }

        generator = ForensicReportGenerator()
        return generator.generate_report(
            case_id=case_id,
            investigation_id=email_data["id"],
            email_data=email_data,
            threat_assessment=threat_assessment,
            header_forensics=header_forensics,
            infrastructure_data=infrastructure_data,
            graph_data=graph_data,
            assigned_analyst=case_info["assigned_to"],
            campaign_data=campaign_data,
        )


# Global Singleton for SIH Demo Provider
sih_demo_service = SIHDemoEnvironment()
