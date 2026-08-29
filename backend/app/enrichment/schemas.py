from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class IndicatorTypeEnum(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    HOSTNAME = "hostname"
    URL = "url"

class IndicatorPriorityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IPClassificationEnum(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    LOOPBACK = "LOOPBACK"
    LINK_LOCAL = "LINK_LOCAL"
    MULTICAST = "MULTICAST"
    RESERVED = "RESERVED"
    INVALID = "INVALID"

class ReputationStatusEnum(str, Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"

class EnrichmentStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class NormalizedIndicatorSchema(BaseModel):
    indicator_id: str = Field(..., description="Unique indicator ID (IND-xxxxxx)")
    type: IndicatorTypeEnum = Field(..., description="Indicator type (ip, domain, hostname, url)")
    value: str = Field(..., description="Normalized indicator value")
    source: str = Field(..., description="Source origin (e.g. received_header, from, reply_to, body)")
    priority: IndicatorPriorityEnum = Field(IndicatorPriorityEnum.MEDIUM, description="Prioritization tier")
    first_seen_in_email: bool = Field(True, description="Whether first observed in this email")
    evidence_reference: Optional[str] = Field(None, description="Forensic rule or hop reference")

class GeolocationSchema(BaseModel):
    country: Optional[str] = Field(None, description="Estimated country name")
    country_code: Optional[str] = Field(None, description="ISO country code")
    region: Optional[str] = Field(None, description="Estimated region/state")
    city: Optional[str] = Field(None, description="Estimated city name")
    latitude: Optional[float] = Field(None, description="Estimated latitude")
    longitude: Optional[float] = Field(None, description="Estimated longitude")
    timezone: Optional[str] = Field(None, description="Timezone name")
    accuracy: str = Field("approximate", description="Accuracy indicator")
    confidence: float = Field(0.80, description="Enrichment confidence (0.0 to 1.0)")
    provider: str = Field("mock_provider", description="Intelligence provider name")

class AnonymizationSchema(BaseModel):
    vpn: Optional[bool] = Field(None, description="VPN detection flag (true/false/null)")
    tor: Optional[bool] = Field(None, description="TOR exit node flag (true/false/null)")
    proxy: Optional[bool] = Field(None, description="Anonymous proxy flag (true/false/null)")
    datacenter: Optional[bool] = Field(None, description="Datacenter/cloud hosting flag")
    residential: Optional[bool] = Field(None, description="Residential ISP flag")

class NetworkInfoSchema(BaseModel):
    asn: Optional[str] = Field(None, description="Autonomous System Number (AS12345)")
    organization: Optional[str] = Field(None, description="AS Organization Name")
    isp: Optional[str] = Field(None, description="Internet Service Provider Name")
    network_type: Optional[str] = Field("hosting", description="hosting, residential, cloud, mobile")

class IPIntelligenceSchema(BaseModel):
    ip: str = Field(..., description="IP address string")
    classification: IPClassificationEnum = Field(..., description="PUBLIC, PRIVATE, etc.")
    network: NetworkInfoSchema = Field(default_factory=NetworkInfoSchema)
    location: GeolocationSchema = Field(default_factory=GeolocationSchema)
    anonymization: AnonymizationSchema = Field(default_factory=AnonymizationSchema)
    reverse_dns: List[str] = Field(default_factory=list, description="PTR record hostnames")
    queried_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class DNSRecordSchema(BaseModel):
    record_type: str = Field(..., description="A, AAAA, MX, NS, CNAME, TXT")
    name: str = Field(..., description="Queried hostname")
    value: str = Field(..., description="Resolved record value")
    ttl: Optional[int] = Field(None, description="Time to live in seconds")

class DomainRegistrationSchema(BaseModel):
    registrar: Optional[str] = Field(None, description="Domain registrar name")
    created_at: Optional[str] = Field(None, description="ISO registration creation timestamp")
    expires_at: Optional[str] = Field(None, description="ISO expiration timestamp")
    updated_at: Optional[str] = Field(None, description="ISO last updated timestamp")
    domain_age_days: Optional[int] = Field(None, description="Calculated domain age in days")
    privacy_protected: Optional[bool] = Field(None, description="WHOIS privacy protection flag")

class DomainIntelligenceSchema(BaseModel):
    domain: str = Field(..., description="Normalized domain name")
    registration: DomainRegistrationSchema = Field(default_factory=DomainRegistrationSchema)
    dns_records: List[DNSRecordSchema] = Field(default_factory=list)
    nameservers: List[str] = Field(default_factory=list)
    mx_records: List[str] = Field(default_factory=list)
    queried_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SingleProviderReputationSchema(BaseModel):
    provider: str = Field(..., description="Provider name (AbuseIPDB, VirusTotal, etc.)")
    status: ReputationStatusEnum = Field(ReputationStatusEnum.UNKNOWN)
    score: Optional[float] = Field(None, description="Abuse score or malicious count")
    confidence: float = Field(0.80, description="Provider confidence")

class ReputationIntelligenceSchema(BaseModel):
    indicator: str = Field(..., description="IP or Domain value")
    indicator_type: str = Field(..., description="ip or domain")
    provider_results: List[SingleProviderReputationSchema] = Field(default_factory=list)
    aggregate_status: ReputationStatusEnum = Field(ReputationStatusEnum.UNKNOWN)
    confidence: float = Field(0.80, description="Aggregate confidence")

class ProbableOriginSchema(BaseModel):
    ip: Optional[str] = Field(None, description="Earliest reliable public IP observed in relay chain")
    location: GeolocationSchema = Field(default_factory=GeolocationSchema)
    confidence: float = Field(0.0, description="Confidence in estimated probable origin (0.0 to 1.0)")
    basis: List[str] = Field(default_factory=list, description="Reasoning basis for origin calculation")
    disclaimer: str = Field(
        "Probable origin represents estimated infrastructure location and does NOT establish physical location or identity of sender.",
        description="Mandatory SIH attribution disclaimer"
    )

class Phase4EnrichmentResponse(BaseModel):
    email_id: str = Field(..., description="Email ID")
    status: EnrichmentStatusEnum = Field(EnrichmentStatusEnum.COMPLETED)
    indicators: List[NormalizedIndicatorSchema] = Field(default_factory=list)
    ip_intelligence: List[IPIntelligenceSchema] = Field(default_factory=list)
    domain_intelligence: List[DomainIntelligenceSchema] = Field(default_factory=list)
    reputation: List[ReputationIntelligenceSchema] = Field(default_factory=list)
    probable_origin: ProbableOriginSchema = Field(default_factory=ProbableOriginSchema)
    disclaimers: List[str] = Field(default_factory=lambda: [
        "Infrastructure intelligence does NOT identify the attacker or real-world person.",
        "Geolocation represents estimated infrastructure location.",
        "Domain registration age is a contextual signal, not proof of malicious intent.",
        "External intelligence is supplemental and does not replace primary email forensic evidence."
    ])
