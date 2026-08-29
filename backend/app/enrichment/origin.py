from typing import List, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.enrichment.schemas import (
    ProbableOriginSchema,
    IPIntelligenceSchema,
    GeolocationSchema,
)

class ProbableOriginClassifier:
    """
    Probable Origin Infrastructure Classifier for MailTrace.
    Correlates Phase 2 relay hop analysis with Phase 4 IP intelligence & anonymization signals
    to calculate probable transmission origin infrastructure and confidence score (0.0 to 1.0).
    """

    @classmethod
    def calculate_probable_origin(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse,
        ip_intel_list: List[IPIntelligenceSchema]
    ) -> ProbableOriginSchema:
        origin_ip = forensics.routing.origin_ip

        if not origin_ip:
            return ProbableOriginSchema(
                ip=None,
                location=GeolocationSchema(country="Unknown", accuracy="approximate", confidence=0.0),
                confidence=0.0,
                basis=["No reliable public IP address observed in Received relay chain."]
            )

        # Match IP intelligence record
        ip_intel: Optional[IPIntelligenceSchema] = None
        for intel in ip_intel_list:
            if intel.ip == origin_ip:
                ip_intel = intel
                break

        basis: List[str] = [
            f"Earliest reliable public IP ({origin_ip}) observed at relay hop #{forensics.routing.origin_hop_index or 1}",
            "Verified Received header timestamp chronological sequence"
        ]

        base_confidence = 0.85

        if ip_intel:
            loc = ip_intel.location
            anon = ip_intel.anonymization

            if anon.tor:
                base_confidence -= 0.35
                basis.append("Origin IP associated with TOR exit node (anonymized infrastructure)")
            elif anon.vpn:
                base_confidence -= 0.25
                basis.append("Origin IP associated with commercial VPN provider")
            elif anon.proxy:
                base_confidence -= 0.20
                basis.append("Origin IP associated with anonymous proxy service")

            if ip_intel.network.isp:
                basis.append(f"Network ISP: {ip_intel.network.isp} ({ip_intel.network.asn or 'AS-UNKNOWN'})")

            final_conf = max(0.20, min(0.95, round(base_confidence, 2)))

            return ProbableOriginSchema(
                ip=origin_ip,
                location=loc,
                confidence=final_conf,
                basis=basis
            )

        return ProbableOriginSchema(
            ip=origin_ip,
            location=GeolocationSchema(country="Unknown", accuracy="approximate", confidence=0.50),
            confidence=0.50,
            basis=basis
        )
