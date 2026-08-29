import uuid
from typing import List, Dict, Set
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.enrichment.schemas import (
    NormalizedIndicatorSchema,
    IndicatorTypeEnum,
    IndicatorPriorityEnum,
)
from app.enrichment.ip_classifier import IPClassifier

class IndicatorPrioritizer:
    """
    Prioritizes and deduplicates security-relevant technical indicators extracted from
    Phase 1 (Normalized Email), Phase 2 (Forensics), and Phase 3 (Threat Analysis).
    """

    @classmethod
    def prioritize_indicators(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse
    ) -> List[NormalizedIndicatorSchema]:
        indicators: List[NormalizedIndicatorSchema] = []
        seen: Set[str] = set()

        # 1. Earliest Reliable Public IP from Received chain (HIGH priority)
        origin_ip = None
        for hop in forensics.relay_analysis.hops:
            if hop.source_ip and IPClassifier.is_enrichable_public_ip(hop.source_ip):
                origin_ip = hop.source_ip
                break

        if origin_ip:
            key = f"ip:{origin_ip}"
            if key not in seen:
                seen.add(key)
                indicators.append(NormalizedIndicatorSchema(
                    indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                    type=IndicatorTypeEnum.IP,
                    value=origin_ip,
                    source="received_header_origin",
                    priority=IndicatorPriorityEnum.HIGH,
                    evidence_reference="earliest_reliable_public_ip"
                ))

        # 2. Sender Domain (HIGH priority)
        if canonical_email.identity.from_:
            from_domain = canonical_email.identity.from_[0].domain.lower()
            if from_domain and from_domain not in ("localhost", "local"):
                key = f"domain:{from_domain}"
                if key not in seen:
                    seen.add(key)
                    indicators.append(NormalizedIndicatorSchema(
                        indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                        type=IndicatorTypeEnum.DOMAIN,
                        value=from_domain,
                        source="from_header",
                        priority=IndicatorPriorityEnum.HIGH,
                        evidence_reference="sender_domain"
                    ))

        # 3. Reply-To Domain (HIGH priority)
        if canonical_email.identity.reply_to:
            reply_domain = canonical_email.identity.reply_to[0].domain.lower()
            if reply_domain and reply_domain not in ("localhost", "local"):
                key = f"domain:{reply_domain}"
                if key not in seen:
                    seen.add(key)
                    indicators.append(NormalizedIndicatorSchema(
                        indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                        type=IndicatorTypeEnum.DOMAIN,
                        value=reply_domain,
                        source="reply_to_header",
                        priority=IndicatorPriorityEnum.HIGH,
                        evidence_reference="reply_to_domain"
                    ))

        # 4. Return-Path Domain (HIGH priority)
        if canonical_email.identity.return_path:
            rp_domain = canonical_email.identity.return_path.domain.lower()
            if rp_domain and rp_domain not in ("localhost", "local"):
                key = f"domain:{rp_domain}"
                if key not in seen:
                    seen.add(key)
                    indicators.append(NormalizedIndicatorSchema(
                        indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                        type=IndicatorTypeEnum.DOMAIN,
                        value=rp_domain,
                        source="return_path_header",
                        priority=IndicatorPriorityEnum.HIGH,
                        evidence_reference="return_path_domain"
                    ))

        # 5. DKIM Signing Domain (MEDIUM priority)
        if forensics.authentication.dkim.signing_domain:
            dkim_domain = forensics.authentication.dkim.signing_domain.lower()
            key = f"domain:{dkim_domain}"
            if key not in seen:
                seen.add(key)
                indicators.append(NormalizedIndicatorSchema(
                    indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                    type=IndicatorTypeEnum.DOMAIN,
                    value=dkim_domain,
                    source="dkim_header",
                    priority=IndicatorPriorityEnum.MEDIUM,
                    evidence_reference="dkim_domain"
                ))

        # 6. Other Public Relay IPs (MEDIUM priority)
        for hop in forensics.relay_analysis.hops:
            if hop.source_ip and IPClassifier.is_enrichable_public_ip(hop.source_ip):
                key = f"ip:{hop.source_ip}"
                if key not in seen:
                    seen.add(key)
                    indicators.append(NormalizedIndicatorSchema(
                        indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                        type=IndicatorTypeEnum.IP,
                        value=hop.source_ip,
                        source="received_relay_hop",
                        priority=IndicatorPriorityEnum.MEDIUM,
                        evidence_reference=f"hop_{hop.hop_order}"
                    ))

        # 7. Suspicious URL Hostnames (HIGH/MEDIUM priority)
        for u in canonical_email.indicators.urls:
            if u.hostname:
                host = u.hostname.lower()
                key = f"domain:{host}"
                if key not in seen:
                    seen.add(key)
                    indicators.append(NormalizedIndicatorSchema(
                        indicator_id=f"IND-{uuid.uuid4().hex[:8]}",
                        type=IndicatorTypeEnum.DOMAIN,
                        value=host,
                        source="url_hostname",
                        priority=IndicatorPriorityEnum.HIGH if u.deceptive else IndicatorPriorityEnum.MEDIUM,
                        evidence_reference=f"url_{u.raw_url[:30]}"
                    ))

        return indicators
