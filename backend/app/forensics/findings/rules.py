import uuid
from typing import List, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import (
    AuthenticationMatrixSchema,
    HeaderAnalysisSchema,
    RelayAnalysisSchema,
    ForensicFindingSchema,
    FindingEvidenceSchema,
    SeverityLevel,
    AuthResultStatus,
)

class ForensicRuleEngine:
    """
    Rule-based deterministic engine evaluating technical anomalies:
    HDR001: From / Reply-To domain mismatch
    HDR002: From / Return-Path domain mismatch
    HDR003: Message-ID domain mismatch
    HDR004: Received timestamp inconsistency
    HDR005: Malformed Received header
    HDR006: Authentication-domain mismatch
    HDR007: Unexpected authentication result
    HDR008: Missing authentication evidence
    HDR009: Relay ordering anomaly
    HDR010: Inconsistent sender identity
    """

    @classmethod
    def evaluate_all(
        cls,
        canonical_email: CanonicalEmailObject,
        auth_matrix: AuthenticationMatrixSchema,
        header_analysis: HeaderAnalysisSchema,
        relay_analysis: RelayAnalysisSchema
    ) -> List[ForensicFindingSchema]:
        findings: List[ForensicFindingSchema] = []

        # HDR001: From / Reply-To domain mismatch
        f1 = cls._evaluate_hdr001(canonical_email, header_analysis)
        if f1:
            findings.append(f1)

        # HDR002: From / Return-Path domain mismatch
        f2 = cls._evaluate_hdr002(canonical_email, header_analysis)
        if f2:
            findings.append(f2)

        # HDR003: Message-ID domain mismatch
        f3 = cls._evaluate_hdr003(canonical_email, header_analysis)
        if f3:
            findings.append(f3)

        # HDR004: Received timestamp inconsistency
        f4 = cls._evaluate_hdr004(relay_analysis)
        if f4:
            findings.append(f4)

        # HDR005: Malformed Received header
        f5 = cls._evaluate_hdr005(relay_analysis)
        if f5:
            findings.append(f5)

        # HDR006: Authentication-domain mismatch
        f6 = cls._evaluate_hdr006(auth_matrix)
        if f6:
            findings.append(f6)

        # HDR007: Unexpected authentication result
        f7 = cls._evaluate_hdr007(auth_matrix)
        if f7:
            findings.append(f7)

        # HDR008: Missing authentication evidence
        f8 = cls._evaluate_hdr008(auth_matrix)
        if f8:
            findings.append(f8)

        # HDR009: Relay ordering anomaly
        f9 = cls._evaluate_hdr009(relay_analysis)
        if f9:
            findings.append(f9)

        # HDR010: Inconsistent sender identity
        f10 = cls._evaluate_hdr010(canonical_email)
        if f10:
            findings.append(f10)

        return findings

    @classmethod
    def _gen_id(cls) -> str:
        return f"FND-{uuid.uuid4().hex[:8]}"

    @classmethod
    def _evaluate_hdr001(cls, canonical: CanonicalEmailObject, headers: HeaderAnalysisSchema) -> Optional[ForensicFindingSchema]:
        if not headers.from_reply_to.match and headers.from_reply_to.domain_b:
            from_addr = canonical.identity.from_[0].address if canonical.identity.from_ else ""
            reply_to_addr = canonical.identity.reply_to[0].address if canonical.identity.reply_to else ""
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR001",
                category="header_anomaly",
                severity=SeverityLevel.MEDIUM,
                title="Reply-To domain differs from visible From domain",
                description="The Reply-To address specifies a different organizational domain than the visible From address.",
                confidence=0.98,
                evidence=[
                    FindingEvidenceSchema(source="From Header", value=from_addr),
                    FindingEvidenceSchema(source="Reply-To Header", value=reply_to_addr)
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr002(cls, canonical: CanonicalEmailObject, headers: HeaderAnalysisSchema) -> Optional[ForensicFindingSchema]:
        if not headers.from_return_path.match and headers.from_return_path.domain_b:
            from_addr = canonical.identity.from_[0].address if canonical.identity.from_ else ""
            return_path = canonical.identity.return_path or ""
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR002",
                category="header_anomaly",
                severity=SeverityLevel.LOW,
                title="From/Return-Path envelope domain mismatch",
                description="Return-Path envelope sender domain differs from visible From address domain (common in bulk mailers/relays).",
                confidence=0.95,
                evidence=[
                    FindingEvidenceSchema(source="From Header", value=from_addr),
                    FindingEvidenceSchema(source="Return-Path Header", value=return_path)
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr003(cls, canonical: CanonicalEmailObject, headers: HeaderAnalysisSchema) -> Optional[ForensicFindingSchema]:
        if not headers.message_id.match and headers.message_id.domain_b:
            from_addr = canonical.identity.from_[0].address if canonical.identity.from_ else ""
            msg_id = canonical.identity.message_id or ""
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR003",
                category="header_anomaly",
                severity=SeverityLevel.LOW,
                title="Message-ID domain differs from visible From domain",
                description="The domain portion of the Message-ID header does not match the visible From domain.",
                confidence=0.92,
                evidence=[
                    FindingEvidenceSchema(source="From Header", value=from_addr),
                    FindingEvidenceSchema(source="Message-ID Header", value=msg_id)
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr004(cls, relay: RelayAnalysisSchema) -> Optional[ForensicFindingSchema]:
        anomalies = relay.timestamp_analysis.get("anomalies", [])
        if anomalies:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR004",
                category="routing_anomaly",
                severity=SeverityLevel.MEDIUM,
                title="Received timestamp sequence anomaly",
                description="One or more Received header timestamps show non-chronological ordering or server clock skew.",
                confidence=0.90,
                evidence=[
                    FindingEvidenceSchema(source="Timestamp Analysis", value="; ".join(anomalies))
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr005(cls, relay: RelayAnalysisSchema) -> Optional[ForensicFindingSchema]:
        for hop in relay.hops:
            if not hop.source_hostname and not hop.source_ip:
                return ForensicFindingSchema(
                    finding_id=cls._gen_id(),
                    rule_id="HDR005",
                    category="routing_anomaly",
                    severity=SeverityLevel.LOW,
                    title="Malformed Received header hop detected",
                    description=f"Received header hop #{hop.hop} lacks recognizable source hostname and IP address metadata.",
                    confidence=0.88,
                    evidence=[
                        FindingEvidenceSchema(source=f"Received Hop #{hop.hop}", value=hop.raw_value)
                    ]
                )
        return None

    @classmethod
    def _evaluate_hdr006(cls, auth: AuthenticationMatrixSchema) -> Optional[ForensicFindingSchema]:
        if auth.dmarc.result == AuthResultStatus.FAIL and not auth.alignment.spf_aligned_relaxed and not auth.alignment.dkim_aligned_relaxed:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR006",
                category="auth_failure",
                severity=SeverityLevel.HIGH,
                title="Authentication-domain alignment failure",
                description="Neither SPF nor DKIM authenticated domains match the visible From header domain.",
                confidence=0.99,
                evidence=[
                    FindingEvidenceSchema(source="From Domain", value=auth.dmarc.header_from_domain or "Unknown"),
                    FindingEvidenceSchema(source="SPF Domain", value=auth.spf.domain or "None"),
                    FindingEvidenceSchema(source="DKIM Domain", value=auth.dkim.signing_domain or "None")
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr007(cls, auth: AuthenticationMatrixSchema) -> Optional[ForensicFindingSchema]:
        failures = []
        if auth.spf.result in (AuthResultStatus.FAIL, AuthResultStatus.SOFTFAIL, AuthResultStatus.PERMERROR):
            failures.append(f"SPF {auth.spf.result.value}")
        if auth.dkim.result in (AuthResultStatus.FAIL, AuthResultStatus.PERMERROR):
            failures.append(f"DKIM {auth.dkim.result.value}")

        if failures:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR007",
                category="auth_failure",
                severity=SeverityLevel.HIGH,
                title="Explicit email authentication check failure",
                description="One or more technical authentication checks (SPF/DKIM) produced an explicit failure verdict.",
                confidence=0.97,
                evidence=[
                    FindingEvidenceSchema(source="Auth Evaluation", value="; ".join(failures))
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr008(cls, auth: AuthenticationMatrixSchema) -> Optional[ForensicFindingSchema]:
        if auth.spf.result == AuthResultStatus.NONE and auth.dkim.result == AuthResultStatus.NONE and not auth.dkim.signature_present:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR008",
                category="auth_anomaly",
                severity=SeverityLevel.INFO,
                title="Missing authentication evidence",
                description="Email payload contains no SPF or DKIM authentication evaluation headers.",
                confidence=1.00,
                evidence=[
                    FindingEvidenceSchema(source="Headers", value="No Authentication-Results or DKIM-Signature headers present")
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr009(cls, relay: RelayAnalysisSchema) -> Optional[ForensicFindingSchema]:
        if len(relay.hops) > 5:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR009",
                category="routing_anomaly",
                severity=SeverityLevel.MEDIUM,
                title="Unusually long relay hop chain",
                description=f"Email traversed an excessive number of SMTP relay hops ({len(relay.hops)} hops).",
                confidence=0.85,
                evidence=[
                    FindingEvidenceSchema(source="Relay Chain", value=f"Total hops: {len(relay.hops)}")
                ]
            )
        return None

    @classmethod
    def _evaluate_hdr010(cls, canonical: CanonicalEmailObject) -> Optional[ForensicFindingSchema]:
        if len(canonical.identity.from_) > 1:
            return ForensicFindingSchema(
                finding_id=cls._gen_id(),
                rule_id="HDR010",
                category="header_anomaly",
                severity=SeverityLevel.MEDIUM,
                title="Multiple From addresses in email header",
                description="The From header contains multiple sender email addresses.",
                confidence=0.96,
                evidence=[
                    FindingEvidenceSchema(source="From Header", value="; ".join([a.address for a in canonical.identity.from_]))
                ]
            )
        return None
