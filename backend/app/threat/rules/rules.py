import uuid
from typing import List, Dict, Any, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.schemas.threat import ThreatSignalSchema, ThreatEvidenceSpanSchema

class DeterministicThreatRules:
    """
    Deterministic rule engine evaluating high-confidence threat patterns:
    THR001: Urgent credential request
    THR002: Financial request + urgency
    THR003: Executive authority + financial request
    THR004: Login request + suspicious URL structure
    THR005: Lookalike domain + credential request
    THR006: Executable attachment + urgent action
    THR007: Authentication anomaly + impersonation indicators
    THR008: Multiple independent phishing signals
    """

    @classmethod
    def evaluate_all(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        feature_vector: Dict[str, Any]
    ) -> List[ThreatSignalSchema]:
        signals: List[ThreatSignalSchema] = []

        content = feature_vector.get("content", {})
        urls = feature_vector.get("url", {})
        attachments = feature_vector.get("attachment", {})
        f_feats = feature_vector.get("forensics", {})

        # THR001: Urgent credential request
        if content.get("has_urgency") and content.get("has_credential_prompt"):
            spans = content.get("urgency_spans", []) + content.get("credential_spans", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR001",
                category="credential_harvesting",
                severity="high",
                score=0.91,
                title="Urgent credential harvesting request",
                description="High-urgency language combined with password or account verification prompt.",
                evidence=[ThreatEvidenceSpanSchema(source="body", text_span=s) for s in spans[:3]]
            ))

        # THR002: Financial request + urgency
        if content.get("has_financial_request") and content.get("has_urgency"):
            spans = content.get("financial_spans", []) + content.get("urgency_spans", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR002",
                category="financial_request",
                severity="high",
                score=0.93,
                title="Urgent financial transaction request",
                description="Payment, wire transfer, or invoice request combined with tight deadline.",
                evidence=[ThreatEvidenceSpanSchema(source="body", text_span=s) for s in spans[:3]]
            ))

        # THR003: Executive authority + financial request
        if content.get("has_authority_claim") and content.get("has_financial_request"):
            spans = content.get("authority_spans", []) + content.get("financial_spans", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR003",
                category="business_email_compromise",
                severity="critical",
                score=0.96,
                title="Executive authority financial request (BEC Pattern)",
                description="Executive title claim combined with financial action or wire transfer request.",
                evidence=[ThreatEvidenceSpanSchema(source="body", text_span=s) for s in spans[:3]]
            ))

        # THR004: Login request + suspicious URL structure
        if content.get("has_credential_prompt") and (urls.get("has_ip_hostname") or urls.get("has_credential_path")):
            susp = urls.get("suspicious_urls", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR004",
                category="phishing",
                severity="high",
                score=0.92,
                title="Login prompt pointing to suspicious URL structure",
                description="Credential prompt directing users to IP-hostnames or non-standard login paths.",
                evidence=[ThreatEvidenceSpanSchema(source="url", text_span=u) for u in susp[:3]]
            ))

        # THR005: Lookalike domain + credential request
        if urls.get("has_lookalike_domain") and content.get("has_credential_prompt"):
            lookalikes = urls.get("lookalike_domains", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR005",
                category="phishing",
                severity="critical",
                score=0.97,
                title="Deceptive lookalike domain with credential prompt",
                description="Domain mimicking known brand combined with credential harvesting prompt.",
                evidence=[ThreatEvidenceSpanSchema(source="url_hostname", text_span=d) for d in lookalikes[:3]]
            ))

        # THR006: Executable attachment + urgent action
        if (attachments.get("has_executable") or attachments.get("has_double_extension")) and content.get("has_urgency"):
            susp_att = attachments.get("suspicious_attachments", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR006",
                category="malicious_delivery",
                severity="high",
                score=0.94,
                title="Executable attachment with urgent call-to-action",
                description="High-risk executable or double-extension attachment combined with urgent body text.",
                evidence=[ThreatEvidenceSpanSchema(source="attachment", text_span=a) for a in susp_att[:3]]
            ))

        # THR007: Authentication anomaly + impersonation indicators
        if (f_feats.get("spf_fail") or f_feats.get("from_reply_to_mismatch")) and content.get("has_authority_claim"):
            spans = content.get("authority_spans", [])
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR007",
                category="impersonation",
                severity="critical",
                score=0.95,
                title="Authentication failure with authority claim",
                description="SPF/Reply-To header anomaly combined with executive or role authority claim.",
                evidence=[ThreatEvidenceSpanSchema(source="header_and_body", text_span=s) for s in spans[:3]]
            ))

        # THR008: Multiple independent phishing signals
        signal_count = len(signals)
        if signal_count >= 2:
            signals.append(ThreatSignalSchema(
                signal_id=f"SIG-{uuid.uuid4().hex[:8]}",
                rule_id="THR008",
                category="multi_signal_threat",
                severity="high",
                score=0.90,
                title="Multiple independent threat signals detected",
                description=f"Email exhibits {signal_count} separate high-confidence threat signals.",
                evidence=[ThreatEvidenceSpanSchema(source="rule_engine", text_span=f"Triggered {signal_count} independent threat rules")]
            ))

        return signals
