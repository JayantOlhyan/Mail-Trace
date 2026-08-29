from datetime import datetime
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.schemas.threat import Phase3ThreatAnalysisResponse
from app.threat.features.vector import FeatureVectorAggregator
from app.threat.rules.rules import DeterministicThreatRules
from app.threat.models.deterministic import DeterministicThreatModel
from app.threat.models.prompt_safety import PromptInjectionFilter
from app.threat.scoring import RiskEngine
from app.threat.explanation import ExplanationBuilder
from app.models.db import (
    EmailTable,
    ThreatAnalysisTable,
    ThreatSignalTable,
    ThreatEvidenceTable,
    ThreatClassificationTable,
)

class Phase3ThreatService:
    """
    Phase 3 Master Orchestrator for AI Threat Detection & Risk Assessment Engine.
    Aggregates features across Phase 1 & 2 -> Executes deterministic rules -> Applies prompt safety ->
    Classifies threat -> Computes 0-100 risk score -> Builds evidence explanation -> Persists to DB.
    """

    @classmethod
    async def analyze_and_persist(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        db: AsyncSession,
        model_override: Optional[Any] = None
    ) -> Phase3ThreatAnalysisResponse:
        email_id = canonical_email.email_id

        # 1. Prompt Injection Defense Filtering on untrusted body content
        sanitized_text = PromptInjectionFilter.sanitize_untrusted_text(canonical_email.content.text_body)
        canonical_email.content.text_body = sanitized_text

        # 2. Extract Feature Vector across Phase 1 + Phase 2 + Phase 3
        feature_vector = FeatureVectorAggregator.aggregate(canonical_email, forensics)

        # 3. Execute Deterministic Threat Rules (THR001 - THR008)
        signals = DeterministicThreatRules.evaluate_all(canonical_email, forensics, feature_vector)

        # 4. Classify Threat via Model Interface (Fallback to Deterministic baseline)
        model = model_override or DeterministicThreatModel()
        classification = model.predict(feature_vector)

        # 5. Calculate 0-100 Risk Score & Level
        risk = RiskEngine.calculate_risk(signals, classification, feature_vector)

        # 6. Build Explainable Assessment & Evidence Spans
        explanation_text, evidence_spans = ExplanationBuilder.build_explanation(classification, risk, signals)

        response = Phase3ThreatAnalysisResponse(
            email_id=email_id,
            analysis={
                "engine_version": "3.0.0",
                "model_version": getattr(model, "version", "deterministic-v1"),
                "analyzed_at": datetime.utcnow().isoformat()
            },
            classification=classification,
            risk=risk,
            signals=signals,
            evidence=evidence_spans,
            explanation=explanation_text
        )

        # 7. Idempotent DB Persistence
        await cls._persist_to_db(response, db)

        return response

    @classmethod
    async def _persist_to_db(cls, response: Phase3ThreatAnalysisResponse, db: AsyncSession) -> None:
        email_id = response.email_id

        # Check if email exists in DB
        email_record = await db.get(EmailTable, email_id)
        if not email_record:
            return  # Skip ORM relations if base email not in DB

        # Clear existing Phase 3 analyses for idempotency
        stmt_t = select(ThreatAnalysisTable).where(ThreatAnalysisTable.email_id == email_id)
        existing_t = (await db.execute(stmt_t)).scalars().all()
        for item in existing_t:
            await db.delete(item)

        # Create Threat Analysis record
        tan_id = f"TAN-{email_id[:12]}"
        analysis_rec = ThreatAnalysisTable(
            id=tan_id,
            email_id=email_id,
            engine_version=response.analysis.get("engine_version", "3.0.0"),
            model_version=response.analysis.get("model_version", "deterministic-v1"),
            primary_class=response.classification.primary.value,
            risk_level=response.risk.level.value,
            risk_score=response.risk.score,
            classification_confidence=response.classification.confidence,
            explanation=response.explanation
        )
        db.add(analysis_rec)

        # Primary Classification
        db.add(ThreatClassificationTable(
            analysis_id=tan_id,
            label=response.classification.primary.value,
            confidence=response.classification.confidence,
            is_primary=True
        ))

        # Secondary Classifications
        for sec in response.classification.secondary:
            db.add(ThreatClassificationTable(
                analysis_id=tan_id,
                label=sec.value,
                confidence=response.classification.confidence * 0.9,
                is_primary=False
            ))

        # Save Threat Signals & Evidence Spans
        for sig in response.signals:
            sig_rec = ThreatSignalTable(
                id=sig.signal_id,
                analysis_id=tan_id,
                signal_type=sig.category,
                rule_id=sig.rule_id,
                severity=sig.severity,
                score=sig.score,
                title=sig.title,
                description=sig.description
            )
            db.add(sig_rec)
            for ev in sig.evidence:
                db.add(ThreatEvidenceTable(
                    signal_id=sig.signal_id,
                    source_type=ev.source,
                    source_reference=ev.reference,
                    text_span=ev.text_span
                ))

        await db.commit()
