from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.enrichment.schemas import (
    Phase4EnrichmentResponse,
    EnrichmentStatusEnum,
    IPIntelligenceSchema,
    DomainIntelligenceSchema,
    ReputationIntelligenceSchema,
    IndicatorTypeEnum,
)
from app.enrichment.prioritizer import IndicatorPrioritizer
from app.enrichment.cache import IntelligenceCache
from app.enrichment.providers.mock import MockIntelligenceProvider
from app.enrichment.origin import ProbableOriginClassifier
from app.models.db import (
    EmailTable,
    InfrastructureIndicatorTable,
    IPIntelligenceTable,
    GeolocationResultTable,
    DomainIntelligenceTable,
    DNSRecordTable,
    ReputationResultTable,
    EnrichmentLookupTable,
)

class Phase4EnrichmentService:
    """
    Phase 4 Master Orchestrator for Infrastructure Intelligence, Geolocation & External Enrichment.
    Extracts & prioritizes indicators -> Queries intelligence cache & providers ->
    Computes probable origin infrastructure -> Idempotently persists to database.
    """

    @classmethod
    async def enrich_and_persist(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        db: AsyncSession,
        provider_override: Optional[Any] = None
    ) -> Phase4EnrichmentResponse:
        email_id = canonical_email.email_id
        provider = provider_override or MockIntelligenceProvider()
        provider_name = getattr(provider, "provider_name", lambda: "mock_provider")()

        # 1. Prioritize and deduplicate indicators
        indicators = IndicatorPrioritizer.prioritize_indicators(canonical_email, forensics)

        ip_intel_list: List[IPIntelligenceSchema] = []
        domain_intel_list: List[DomainIntelligenceSchema] = []
        reputation_list: List[ReputationIntelligenceSchema] = []

        # 2. Enrich prioritized indicators using cache & provider abstraction
        for ind in indicators:
            cache_key = f"{provider_name}:{ind.type.value}:{ind.value}"
            cached_res = IntelligenceCache.get(cache_key)

            if cached_res:
                if ind.type == IndicatorTypeEnum.IP:
                    ip_intel_list.append(cached_res["ip"])
                elif ind.type in (IndicatorTypeEnum.DOMAIN, IndicatorTypeEnum.HOSTNAME):
                    domain_intel_list.append(cached_res["domain"])
                continue

            # Execute provider lookup
            if ind.type == IndicatorTypeEnum.IP:
                res_ip = await provider.lookup_ip(ind.value)
                if res_ip:
                    ip_intel_list.append(res_ip)
                    res_rep = await provider.lookup_reputation(ind.value, "ip")
                    if res_rep:
                        reputation_list.append(res_rep)
                    IntelligenceCache.set(cache_key, {"ip": res_ip, "rep": res_rep}, ttl_seconds=3600)

            elif ind.type in (IndicatorTypeEnum.DOMAIN, IndicatorTypeEnum.HOSTNAME):
                res_dom = await provider.lookup_domain(ind.value)
                if res_dom:
                    domain_intel_list.append(res_dom)
                    res_rep = await provider.lookup_reputation(ind.value, "domain")
                    if res_rep:
                        reputation_list.append(res_rep)
                    IntelligenceCache.set(cache_key, {"domain": res_dom, "rep": res_rep}, ttl_seconds=3600)

        # 3. Calculate Probable Origin Infrastructure
        probable_origin = ProbableOriginClassifier.calculate_probable_origin(canonical_email, forensics, ip_intel_list)

        response = Phase4EnrichmentResponse(
            email_id=email_id,
            status=EnrichmentStatusEnum.COMPLETED,
            indicators=indicators,
            ip_intelligence=ip_intel_list,
            domain_intelligence=domain_intel_list,
            reputation=reputation_list,
            probable_origin=probable_origin
        )

        # 4. Idempotent DB Persistence
        await cls._persist_to_db(response, db)

        return response

    @classmethod
    async def _persist_to_db(cls, response: Phase4EnrichmentResponse, db: AsyncSession) -> None:
        email_id = response.email_id

        email_record = await db.get(EmailTable, email_id)
        if not email_record:
            return

        # Clear existing indicators for idempotency
        stmt = select(InfrastructureIndicatorTable).where(InfrastructureIndicatorTable.email_id == email_id)
        existing = (await db.execute(stmt)).scalars().all()
        for item in existing:
            await db.delete(item)

        # Save Indicators and Enrichment Records
        for ind in response.indicators:
            ind_rec = InfrastructureIndicatorTable(
                id=ind.indicator_id,
                email_id=email_id,
                indicator_type=ind.type.value,
                indicator_value=ind.value,
                source=ind.source,
                priority=ind.priority.value,
                evidence_reference=ind.evidence_reference
            )
            db.add(ind_rec)

            # Persist IP Intelligence
            for ip_intel in response.ip_intelligence:
                if ip_intel.ip == ind.value:
                    ip_rec = IPIntelligenceTable(
                        indicator_id=ind.indicator_id,
                        ip=ip_intel.ip,
                        classification=ip_intel.classification.value,
                        asn=ip_intel.network.asn,
                        organization=ip_intel.network.organization,
                        isp=ip_intel.network.isp,
                        network_type=ip_intel.network.network_type,
                        reverse_dns=",".join(ip_intel.reverse_dns),
                        cloud=True if ip_intel.network.network_type == "cloud" else False,
                        datacenter=ip_intel.anonymization.datacenter,
                        vpn=ip_intel.anonymization.vpn,
                        tor=ip_intel.anonymization.tor,
                        proxy=ip_intel.anonymization.proxy,
                        provider=ip_intel.location.provider
                    )
                    db.add(ip_rec)
                    await db.flush()

                    loc = ip_intel.location
                    geo_rec = GeolocationResultTable(
                        ip_intelligence_id=ip_rec.id,
                        country=loc.country,
                        country_code=loc.country_code,
                        region=loc.region,
                        city=loc.city,
                        latitude=loc.latitude,
                        longitude=loc.longitude,
                        timezone=loc.timezone,
                        accuracy=loc.accuracy,
                        confidence=loc.confidence,
                        provider=loc.provider
                    )
                    db.add(geo_rec)

            # Persist Domain Intelligence
            for dom_intel in response.domain_intelligence:
                if dom_intel.domain == ind.value:
                    dom_rec = DomainIntelligenceTable(
                        indicator_id=ind.indicator_id,
                        domain=dom_intel.domain,
                        registrar=dom_intel.registration.registrar,
                        created_at_date=dom_intel.registration.created_at,
                        expires_at_date=dom_intel.registration.expires_at,
                        updated_at_date=dom_intel.registration.updated_at,
                        domain_age_days=dom_intel.registration.domain_age_days,
                        privacy_protected=dom_intel.registration.privacy_protected,
                        provider="mock_intelligence_provider"
                    )
                    db.add(dom_rec)
                    await db.flush()

                    for dns in dom_intel.dns_records:
                        db.add(DNSRecordTable(
                            domain_intelligence_id=dom_rec.id,
                            record_type=dns.record_type,
                            name=dns.name,
                            value=dns.value,
                            ttl=dns.ttl
                        ))

            # Persist Reputation
            for rep in response.reputation:
                if rep.indicator == ind.value:
                    for pr in rep.provider_results:
                        db.add(ReputationResultTable(
                            indicator_id=ind.indicator_id,
                            provider=pr.provider,
                            status=pr.status.value,
                            score=pr.score,
                            confidence=pr.confidence
                        ))

        await db.commit()
