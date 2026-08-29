from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class AuthStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SOFTFAIL = "SOFTFAIL"
    NEUTRAL = "NEUTRAL"
    NONE = "NONE"

class DMARCPolicy(str, Enum):
    REJECT = "reject"
    QUARANTINE = "quarantine"
    NONE = "none"
    ABSENT = "absent"

class SPFResult(BaseModel):
    status: AuthStatus = Field(AuthStatus.NONE, description="SPF authentication status")
    domain: Optional[str] = Field(None, description="Domain checked for SPF")
    sender_ip: Optional[str] = Field(None, description="IP evaluated for SPF")
    reason: str = Field("", description="Explanation of SPF evaluation result")

class DKIMResult(BaseModel):
    status: AuthStatus = Field(AuthStatus.NONE, description="DKIM verification status")
    domain: Optional[str] = Field(None, description="Signing domain in DKIM signature")
    selector: Optional[str] = Field(None, description="DKIM selector used")
    signature_present: bool = Field(False, description="Whether a DKIM-Signature header was present")
    reason: str = Field("", description="Explanation of DKIM result")

class DMARCResult(BaseModel):
    status: AuthStatus = Field(AuthStatus.NONE, description="DMARC compliance status")
    policy: DMARCPolicy = Field(DMARCPolicy.ABSENT, description="Enforced DMARC policy")
    align_spf: bool = Field(False, description="DMARC SPF alignment status")
    align_dkim: bool = Field(False, description="DMARC DKIM alignment status")
    reason: str = Field("", description="Explanation of DMARC result")

class SpoofingAnalysis(BaseModel):
    is_display_name_spoofed: bool = Field(False, description="Display name impersonates trusted entity")
    is_reply_to_mismatched: bool = Field(False, description="Reply-To differs from From address domain")
    is_return_path_mismatched: bool = Field(False, description="Return-Path envelope sender differs from From address")
    impersonated_name: Optional[str] = Field(None, description="Detected executive/entity name being impersonated")
    reasons: List[str] = Field(default_factory=list, description="Specific spoofing indicators flagged")

class AuthenticationVerdict(BaseModel):
    spf: SPFResult = Field(default_factory=SPFResult)
    dkim: DKIMResult = Field(default_factory=DKIMResult)
    dmarc: DMARCResult = Field(default_factory=DMARCResult)
    spoofing: SpoofingAnalysis = Field(default_factory=SpoofingAnalysis)
    is_fully_authenticated: bool = Field(False, description="Whether all email auth protocols pass aligned")
    overall_auth_risk_score: int = Field(0, description="Auth risk contribution score 0-100")

class HopAnalysisResult(BaseModel):
    observed_origin_ip: Optional[str] = Field(None, description="Earliest reliable public relay IP address")
    probable_origin_infrastructure: str = Field("Unknown Infrastructure", description="Inferred ASN/ISP/Hosting infrastructure")
    total_hops: int = Field(0, description="Total number of SMTP Received hops")
    untrusted_hops_count: int = Field(0, description="Count of untrusted public relays")
    relay_anomalies: List[str] = Field(default_factory=list, description="Routing anomalies or timestamp inconsistencies")
