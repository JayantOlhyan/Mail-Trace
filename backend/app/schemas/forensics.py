from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class AuthResultStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SOFTFAIL = "SOFTFAIL"
    NEUTRAL = "NEUTRAL"
    NONE = "NONE"
    TEMPERROR = "TEMPERROR"
    PERMERROR = "PERMERROR"

class DMARCPolicyEnum(str, Enum):
    REJECT = "reject"
    QUARANTINE = "quarantine"
    NONE = "none"
    ABSENT = "absent"

class SeverityLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SPFAnalysisSchema(BaseModel):
    result: AuthResultStatus = Field(AuthResultStatus.NONE, description="SPF evaluation result")
    domain: Optional[str] = Field(None, description="Evaluated domain")
    client_ip: Optional[str] = Field(None, description="Client IP evaluated")
    evaluating_server: Optional[str] = Field(None, description="Server that evaluated SPF")
    source_header: str = Field("Authentication-Results", description="Source header name")
    raw_evidence: Optional[str] = Field(None, description="Raw header snippet")

class DKIMAnalysisSchema(BaseModel):
    result: AuthResultStatus = Field(AuthResultStatus.NONE, description="DKIM evaluation result")
    signing_domain: Optional[str] = Field(None, description="DKIM signing domain (d=)")
    selector: Optional[str] = Field(None, description="DKIM selector (s=)")
    algorithm: Optional[str] = Field(None, description="Algorithm used (a=)")
    canonicalization: Optional[str] = Field(None, description="Canonicalization (c=)")
    signed_headers: List[str] = Field(default_factory=list, description="Signed header list (h=)")
    body_hash: Optional[str] = Field(None, description="Body hash (bh=)")
    signature_present: bool = Field(False, description="Whether DKIM-Signature header exists")
    source_header: str = Field("DKIM-Signature", description="Source header name")
    raw_evidence: Optional[str] = Field(None, description="Raw signature header")

class DMARCAnalysisSchema(BaseModel):
    result: AuthResultStatus = Field(AuthResultStatus.NONE, description="DMARC compliance status")
    header_from_domain: Optional[str] = Field(None, description="From header domain")
    evaluated_domain: Optional[str] = Field(None, description="Evaluated DMARC domain")
    policy: DMARCPolicyEnum = Field(DMARCPolicyEnum.ABSENT, description="Enforced policy")
    spf_aligned: Optional[bool] = Field(None, description="SPF domain alignment status")
    dkim_aligned: Optional[bool] = Field(None, description="DKIM domain alignment status")
    raw_evidence: Optional[str] = Field(None, description="Raw DMARC evaluation evidence")

class ARCAnalysisSchema(BaseModel):
    present: bool = Field(False, description="Whether ARC headers exist")
    result: Optional[AuthResultStatus] = Field(None, description="ARC evaluation result")
    seal_present: bool = Field(False, description="ARC-Seal header presence")
    signature_present: bool = Field(False, description="ARC-Message-Signature presence")
    raw_evidence: Optional[str] = Field(None, description="Raw ARC headers snippet")

class AlignmentSchema(BaseModel):
    spf_aligned_strict: bool = Field(False, description="Exact domain match for SPF")
    spf_aligned_relaxed: bool = Field(False, description="Organizational domain match for SPF")
    dkim_aligned_strict: bool = Field(False, description="Exact domain match for DKIM")
    dkim_aligned_relaxed: bool = Field(False, description="Organizational domain match for DKIM")

class AuthenticationMatrixSchema(BaseModel):
    spf: SPFAnalysisSchema = Field(default_factory=SPFAnalysisSchema)
    dkim: DKIMAnalysisSchema = Field(default_factory=DKIMAnalysisSchema)
    dmarc: DMARCAnalysisSchema = Field(default_factory=DMARCAnalysisSchema)
    arc: ARCAnalysisSchema = Field(default_factory=ARCAnalysisSchema)
    alignment: AlignmentSchema = Field(default_factory=AlignmentSchema)

class DomainComparisonSchema(BaseModel):
    match: bool = Field(True, description="Whether domains align")
    domain_a: Optional[str] = Field(None, description="First domain")
    domain_b: Optional[str] = Field(None, description="Second domain")
    note: str = Field("", description="Explanation of comparison result")

class HeaderAnalysisSchema(BaseModel):
    from_reply_to: DomainComparisonSchema = Field(default_factory=DomainComparisonSchema)
    from_return_path: DomainComparisonSchema = Field(default_factory=DomainComparisonSchema)
    message_id: DomainComparisonSchema = Field(default_factory=DomainComparisonSchema)
    sender_domains: List[str] = Field(default_factory=list, description="Unique sender domains across headers")

class RelayHopAnalysisSchema(BaseModel):
    hop: int = Field(..., description="1-indexed hop order")
    source_hostname: Optional[str] = Field(None, description="Sending hostname")
    source_ip: Optional[str] = Field(None, description="Sending IP address")
    destination: Optional[str] = Field(None, description="Receiving hostname/IP")
    protocol: Optional[str] = Field(None, description="SMTP transfer protocol")
    timestamp: Optional[str] = Field(None, description="Parsed ISO timestamp")
    raw_value: str = Field(..., description="Raw Received header")

class RelayAnalysisSchema(BaseModel):
    hops: List[RelayHopAnalysisSchema] = Field(default_factory=list, description="Relay chain hops")
    timestamp_analysis: Dict[str, Any] = Field(default_factory=dict, description="Timestamp consistency analysis")
    anomalies: List[str] = Field(default_factory=list, description="Relay routing anomalies")

class FindingEvidenceSchema(BaseModel):
    source: str = Field(..., description="Source context or header name")
    value: str = Field(..., description="Observed evidence value")
    raw_reference: Optional[str] = Field(None, description="Original raw snippet")

class ForensicFindingSchema(BaseModel):
    finding_id: str = Field(..., description="Unique finding ID (FND-xxxxxx)")
    rule_id: str = Field(..., description="Rule ID (e.g. HDR001)")
    category: str = Field(..., description="Category (header_anomaly, auth_failure, routing_anomaly)")
    severity: SeverityLevel = Field(..., description="INFO, LOW, MEDIUM, HIGH, CRITICAL")
    title: str = Field(..., description="Short finding title")
    description: str = Field(..., description="Detailed technical description")
    confidence: float = Field(..., description="Technical observation confidence (0.0 to 1.0)")
    evidence: List[FindingEvidenceSchema] = Field(default_factory=list, description="Evidence list")

class TimelineEventSchema(BaseModel):
    event_id: str = Field(..., description="Unique event ID (TLE-xxxxxx)")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")
    event_type: str = Field(..., description="Event type category")
    description: str = Field(..., description="Human-readable event description")
    evidence_reference: Optional[str] = Field(None, description="Reference to source header/hop")
    source: str = Field(..., description="Source name")

class Phase2ForensicAnalysisResponse(BaseModel):
    email_id: str = Field(..., description="Email ID")
    authentication: AuthenticationMatrixSchema = Field(default_factory=AuthenticationMatrixSchema)
    header_analysis: HeaderAnalysisSchema = Field(default_factory=HeaderAnalysisSchema)
    relay_analysis: RelayAnalysisSchema = Field(default_factory=RelayAnalysisSchema)
    findings: List[ForensicFindingSchema] = Field(default_factory=list)
    timeline: List[TimelineEventSchema] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=lambda: {
        "engine_version": "2.0.0",
        "analyzed_at": datetime.utcnow().isoformat()
    })
