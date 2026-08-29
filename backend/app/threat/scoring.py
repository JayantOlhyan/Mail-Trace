from typing import List, Dict, Any
from app.schemas.threat import (
    ThreatRiskAssessmentSchema,
    ThreatRiskLevelEnum,
    ThreatSignalSchema,
    ThreatClassificationSchema,
)

class RiskEngine:
    """
    Centralized 0-100 Risk Engine for MailTrace.
    Computes a weighted, capped, de-duplicated risk score across content, URL, attachment,
    header forensic, and rule-based threat signals.
    """

    @classmethod
    def calculate_risk(
        cls,
        signals: List[ThreatSignalSchema],
        classification: ThreatClassificationSchema,
        feature_vector: Dict[str, Any]
    ) -> ThreatRiskAssessmentSchema:
        score = 0.0

        # Base contribution from signals (capped at 65 points)
        signal_score = 0.0
        seen_categories = set()
        for sig in signals:
            if sig.category not in seen_categories:
                seen_categories.add(sig.category)
                if sig.severity == "critical":
                    signal_score += 25
                elif sig.severity == "high":
                    signal_score += 18
                elif sig.severity == "medium":
                    signal_score += 10
        score += min(65.0, signal_score)

        # Base contribution from Primary Classification label
        p_label = classification.primary.value
        if p_label in ("BUSINESS_EMAIL_COMPROMISE", "CREDENTIAL_HARVESTING", "PHISHING", "MALICIOUS_DELIVERY"):
            score += 25.0
        elif p_label in ("FINANCIAL_FRAUD", "IMPERSONATION"):
            score += 15.0

        # Contribution from Phase 2 Forensic anomalies (capped at 25 points)
        f_feats = feature_vector.get("forensics", {})
        forensic_score = 0.0
        if f_feats.get("dmarc_fail"):
            forensic_score += 12
        elif f_feats.get("spf_fail"):
            forensic_score += 8

        if f_feats.get("from_reply_to_mismatch"):
            forensic_score += 15

        score += min(25.0, forensic_score)

        # Contribution from URL & Attachment structural signals (capped at 20 points)
        urls = feature_vector.get("url", {})
        atts = feature_vector.get("attachment", {})
        struct_score = 0.0
        if urls.get("has_lookalike_domain"):
            struct_score += 15
        if atts.get("has_executable") or atts.get("has_double_extension"):
            struct_score += 15

        score += min(20.0, struct_score)

        # Final score calculation (normalized 0 to 100)
        final_score = int(min(100.0, round(score)))

        # Assign Risk Level
        if final_score >= 80:
            level = ThreatRiskLevelEnum.CRITICAL
        elif final_score >= 60:
            level = ThreatRiskLevelEnum.HIGH
        elif final_score >= 30:
            level = ThreatRiskLevelEnum.MEDIUM
        else:
            level = ThreatRiskLevelEnum.LOW

        confidence = max(classification.confidence, 0.85 if signals else 0.90)

        return ThreatRiskAssessmentSchema(
            level=level,
            score=final_score,
            confidence=confidence
        )
