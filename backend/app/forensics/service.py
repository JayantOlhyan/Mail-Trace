from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import (
    Phase2ForensicAnalysisResponse,
    AuthenticationMatrixSchema,
)
from app.forensics.authentication.spf import SPFAnalyzer
from app.forensics.authentication.dkim import DKIMAnalyzer
from app.forensics.authentication.dmarc import DMARCAnalyzer
from app.forensics.authentication.arc import ARCAnalyzer
from app.forensics.authentication.alignment import DomainAlignmentAnalyzer
from app.forensics.headers.comparisons import HeaderComparisonAnalyzer
from app.forensics.routing.received import ReceivedRoutingAnalyzer
from app.forensics.findings.rules import ForensicRuleEngine
from app.forensics.timeline import ForensicTimelineBuilder
from app.models.db import (
    EmailTable,
    AuthenticationResultTable,
    ForensicFindingTable,
    FindingEvidenceTable,
    RelayHopTable,
    ForensicTimelineEventTable,
)

class Phase2ForensicsService:
    """
    Phase 2 Master Orchestrator for Email Forensics & Authentication Analysis.
    Transforming Canonical Email Object -> Authentication Matrix -> Header Comparisons -> Relay Chain -> Findings -> Timeline.
    Idempotent database persistence.
    """

    @classmethod
    async def analyze_and_persist(
        cls,
        canonical_email: CanonicalEmailObject,
        db: AsyncSession
    ) -> Phase2ForensicAnalysisResponse:
        email_id = canonical_email.email_id

        # 1. Run Authentication Analyzers
        spf = SPFAnalyzer.analyze(canonical_email)
        dkim = DKIMAnalyzer.analyze(canonical_email)
        dmarc = DMARCAnalyzer.analyze(canonical_email, spf.domain, dkim.signing_domain)
        arc = ARCAnalyzer.analyze(canonical_email)
        alignment = DomainAlignmentAnalyzer.evaluate_alignment(
            dmarc.header_from_domain,
            spf.domain,
            dkim.signing_domain
        )

        auth_matrix = AuthenticationMatrixSchema(
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            arc=arc,
            alignment=alignment
        )

        # 2. Run Header Comparison Analyzers
        header_analysis = HeaderComparisonAnalyzer.analyze(canonical_email)

        # 3. Run Received Hop Routing & Timestamp Analyzers
        relay_analysis = ReceivedRoutingAnalyzer.analyze(canonical_email)

        # 4. Execute Deterministic Forensic Rule Engine (HDR001 - HDR010)
        findings = ForensicRuleEngine.evaluate_all(
            canonical_email,
            auth_matrix,
            header_analysis,
            relay_analysis
        )

        # 5. Build Chronological Forensic Timeline
        timeline = ForensicTimelineBuilder.build_timeline(canonical_email, relay_analysis)

        response = Phase2ForensicAnalysisResponse(
            email_id=email_id,
            authentication=auth_matrix,
            header_analysis=header_analysis,
            relay_analysis=relay_analysis,
            findings=findings,
            timeline=timeline
        )

        # 6. Idempotent DB Persistence
        await cls._persist_to_db(response, db)

        return response

    @classmethod
    async def _persist_to_db(cls, response: Phase2ForensicAnalysisResponse, db: AsyncSession) -> None:
        email_id = response.email_id

        # Check if email exists in DB
        email_record = await db.get(EmailTable, email_id)
        if not email_record:
            return  # If not yet persisted in emails table, skip ORM relations

        # Clear any existing Phase 2 results for idempotency
        stmt_auth = select(AuthenticationResultTable).where(AuthenticationResultTable.email_id == email_id)
        existing_auth = (await db.execute(stmt_auth)).scalars().all()
        for item in existing_auth:
            await db.delete(item)

        stmt_find = select(ForensicFindingTable).where(ForensicFindingTable.email_id == email_id)
        existing_find = (await db.execute(stmt_find)).scalars().all()
        for item in existing_find:
            await db.delete(item)

        stmt_hops = select(RelayHopTable).where(RelayHopTable.email_id == email_id)
        existing_hops = (await db.execute(stmt_hops)).scalars().all()
        for item in existing_hops:
            await db.delete(item)

        stmt_tl = select(ForensicTimelineEventTable).where(ForensicTimelineEventTable.email_id == email_id)
        existing_tl = (await db.execute(stmt_tl)).scalars().all()
        for item in existing_tl:
            await db.delete(item)

        # Save Authentication Results
        auth = response.authentication
        db.add(AuthenticationResultTable(
            email_id=email_id,
            mechanism="spf",
            result=auth.spf.result.value,
            domain=auth.spf.domain,
            client_ip=auth.spf.client_ip,
            source=auth.spf.source_header,
            raw_value=auth.spf.raw_evidence
        ))
        db.add(AuthenticationResultTable(
            email_id=email_id,
            mechanism="dkim",
            result=auth.dkim.result.value,
            domain=auth.dkim.signing_domain,
            selector=auth.dkim.selector,
            source=auth.dkim.source_header,
            raw_value=auth.dkim.raw_evidence
        ))
        db.add(AuthenticationResultTable(
            email_id=email_id,
            mechanism="dmarc",
            result=auth.dmarc.result.value,
            domain=auth.dmarc.evaluated_domain,
            source="Authentication-Results",
            raw_value=auth.dmarc.raw_evidence
        ))

        # Save Relay Hops
        for hop in response.relay_analysis.hops:
            db.add(RelayHopTable(
                email_id=email_id,
                hop_number=hop.hop,
                source_hostname=hop.source_hostname,
                source_ip=hop.source_ip,
                destination=hop.destination,
                protocol=hop.protocol,
                timestamp=hop.timestamp,
                raw_value=hop.raw_value
            ))

        # Save Findings & Evidence Items
        for fnd in response.findings:
            finding_rec = ForensicFindingTable(
                id=fnd.finding_id,
                email_id=email_id,
                rule_id=fnd.rule_id,
                category=fnd.category,
                severity=fnd.severity.value,
                title=fnd.title,
                description=fnd.description,
                confidence=fnd.confidence
            )
            db.add(finding_rec)
            for ev in fnd.evidence:
                db.add(FindingEvidenceTable(
                    finding_id=fnd.finding_id,
                    source_type=ev.source,
                    source_reference=ev.value,
                    raw_value=ev.raw_reference
                ))

        # Save Timeline Events
        for tle in response.timeline:
            db.add(ForensicTimelineEventTable(
                id=tle.event_id,
                email_id=email_id,
                event_type=tle.event_type,
                timestamp=tle.timestamp,
                description=tle.description,
                evidence_reference=tle.evidence_reference
            ))

        await db.commit()
