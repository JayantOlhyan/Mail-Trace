from datetime import datetime, timedelta
from typing import Optional
from app.enrichment.schemas import (
    IPIntelligenceSchema,
    IPClassificationEnum,
    NetworkInfoSchema,
    GeolocationSchema,
    AnonymizationSchema,
    DomainIntelligenceSchema,
    DomainRegistrationSchema,
    DNSRecordSchema,
    ReputationIntelligenceSchema,
    SingleProviderReputationSchema,
    ReputationStatusEnum,
)
from app.enrichment.providers.base import (
    IPIntelligenceProvider,
    DomainIntelligenceProvider,
    ReputationProvider,
)

class MockIntelligenceProvider(IPIntelligenceProvider, DomainIntelligenceProvider, ReputationProvider):
    """
    Offline/Mock Intelligence Provider for ThreatTrace AI.
    Provides fast, deterministic IP, Domain, and Reputation enrichment without external network requests.
    """

    def provider_name(self) -> str:
        return "mock_intelligence_provider"

    async def lookup_ip(self, ip: str) -> Optional[IPIntelligenceSchema]:
        is_tor = "185." in ip or "tor" in ip.lower()
        is_vpn = "198." in ip or "vpn" in ip.lower()
        is_proxy = "203." in ip

        country = "India" if "203." in ip else ("Germany" if is_tor else "United States")
        country_code = "IN" if "203." in ip else ("DE" if is_tor else "US")
        city = "Delhi" if "203." in ip else ("Frankfurt" if is_tor else "Ashburn")

        return IPIntelligenceSchema(
            ip=ip,
            classification=IPClassificationEnum.PUBLIC,
            network=NetworkInfoSchema(
                asn="AS13335" if "1.1.1.1" in ip else "AS16509",
                organization="Amazon Web Services" if "198." in ip else "Cloudflare, Inc.",
                isp="Cloudflare, Inc." if "1.1.1.1" in ip else "Amazon.com, Inc.",
                network_type="hosting" if (is_tor or is_vpn) else "cloud"
            ),
            location=GeolocationSchema(
                country=country,
                country_code=country_code,
                region="Delhi NCR" if country_code == "IN" else "Hesse",
                city=city,
                latitude=28.6139 if country_code == "IN" else 50.1109,
                longitude=77.2090 if country_code == "IN" else 8.6821,
                timezone="Asia/Kolkata" if country_code == "IN" else "Europe/Berlin",
                accuracy="approximate",
                confidence=0.85,
                provider="mock_intelligence_provider"
            ),
            anonymization=AnonymizationSchema(
                vpn=is_vpn,
                tor=is_tor,
                proxy=is_proxy,
                datacenter=True,
                residential=False
            ),
            reverse_dns=[f"mail-out-{ip.replace('.', '-')}.provider.net"]
        )

    async def lookup_domain(self, domain: str) -> Optional[DomainIntelligenceSchema]:
        d_lower = domain.lower()
        created_date = (datetime.utcnow() - timedelta(days=12 if "lookalike" in d_lower or "paypa1" in d_lower else 3650)).isoformat()
        age_days = 12 if ("lookalike" in d_lower or "paypa1" in d_lower) else 3650

        return DomainIntelligenceSchema(
            domain=domain,
            registration=DomainRegistrationSchema(
                registrar="Namecheap, Inc." if age_days == 12 else "MarkMonitor Inc.",
                created_at=created_date,
                expires_at=(datetime.utcnow() + timedelta(days=353)).isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                domain_age_days=age_days,
                privacy_protected=True if age_days == 12 else False
            ),
            dns_records=[
                DNSRecordSchema(record_type="A", name=domain, value="203.0.113.10", ttl=300),
                DNSRecordSchema(record_type="MX", name=domain, value=f"mail.{domain}", ttl=300),
                DNSRecordSchema(record_type="TXT", name=domain, value="v=spf1 include:_spf.google.com ~all", ttl=300)
            ],
            nameservers=[f"ns1.{domain}", f"ns2.{domain}"],
            mx_records=[f"mail.{domain}"]
        )

    async def lookup_reputation(self, indicator: str, indicator_type: str) -> Optional[ReputationIntelligenceSchema]:
        ind_lower = indicator.lower()
        is_bad = "evil" in ind_lower or "paypa1" in ind_lower or "lookalike" in ind_lower or "185." in ind_lower

        status = ReputationStatusEnum.MALICIOUS if is_bad else ReputationStatusEnum.CLEAN
        score = 95.0 if is_bad else 0.0

        return ReputationIntelligenceSchema(
            indicator=indicator,
            indicator_type=indicator_type,
            provider_results=[
                SingleProviderReputationSchema(
                    provider="AbuseIPDB_Mock",
                    status=status,
                    score=score,
                    confidence=0.90
                ),
                SingleProviderReputationSchema(
                    provider="VirusTotal_Mock",
                    status=status,
                    score=12.0 if is_bad else 0.0,
                    confidence=0.88
                )
            ],
            aggregate_status=status,
            confidence=0.89
        )
