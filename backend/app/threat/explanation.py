from typing import List
from app.schemas.threat import (
    ThreatClassificationSchema,
    ThreatRiskAssessmentSchema,
    ThreatSignalSchema,
    ThreatEvidenceSpanSchema,
)

class ExplanationBuilder:
    """
    Generates human-analyst explainable threat assessments grounded in empirical evidence.
    Ensures every claim explicitly references observed text spans or Phase 2 findings.
    """

    @classmethod
    def build_explanation(
        cls,
        classification: ThreatClassificationSchema,
        risk: ThreatRiskAssessmentSchema,
        signals: List[ThreatSignalSchema]
    ) -> tuple[str, List[ThreatEvidenceSpanSchema]]:
        all_evidence: List[ThreatEvidenceSpanSchema] = []
        explanation_parts: List[str] = []

        primary = classification.primary.value.replace("_", " ").title()
        explanation_parts.append(
            f"Email classified as {primary} with {risk.level.value} risk score ({risk.score}/100, confidence {classification.confidence:.2f})."
        )

        if signals:
            explanation_parts.append(f"Identified {len(signals)} technical threat signals:")
            for sig in signals:
                explanation_parts.append(f"- [{sig.severity.upper()}] {sig.title}: {sig.description}")
                for ev in sig.evidence:
                    all_evidence.append(ev)
        else:
            explanation_parts.append("No active threat signals or security anomalies detected.")

        full_explanation = "\n".join(explanation_parts)

        # De-duplicate evidence spans
        unique_evidence: List[ThreatEvidenceSpanSchema] = []
        seen = set()
        for ev in all_evidence:
            key = f"{ev.source}:{ev.text_span}"
            if key not in seen:
                seen.add(key)
                unique_evidence.append(ev)

        return full_explanation, unique_evidence
