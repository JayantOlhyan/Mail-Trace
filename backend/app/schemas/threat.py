from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ThreatCategoryEnum(str, Enum):
    LEGITIMATE = "LEGITIMATE"
    SUSPICIOUS = "SUSPICIOUS"
    PHISHING = "PHISHING"
    IMPERSONATION = "IMPERSONATION"
    BUSINESS_EMAIL_COMPROMISE = "BUSINESS_EMAIL_COMPROMISE"
    FINANCIAL_FRAUD = "FINANCIAL_FRAUD"
    CREDENTIAL_HARVESTING = "CREDENTIAL_HARVESTING"
    MALICIOUS_DELIVERY = "MALICIOUS_DELIVERY"
    UNKNOWN = "UNKNOWN"

class ThreatRiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ThreatEvidenceSpanSchema(BaseModel):
    source: str = Field(..., description="Source context (e.g. body, header, url)")
    text_span: str = Field(..., description="Extracted suspicious text span or URL string")
    reference: Optional[str] = Field(None, description="Reference ID or header key")

class ThreatSignalSchema(BaseModel):
    signal_id: str = Field(..., description="Unique signal ID (SIG-xxxxxx)")
    rule_id: Optional[str] = Field(None, description="Rule ID (e.g. THR001) if triggered by rule")
    category: str = Field(..., description="Signal category (urgency, credential, financial, authority)")
    severity: str = Field(..., description="info, low, medium, high, critical")
    score: float = Field(..., description="Signal intensity score (0.0 to 1.0)")
    title: str = Field(..., description="Short signal title")
    description: str = Field(..., description="Detailed technical description")
    evidence: List[ThreatEvidenceSpanSchema] = Field(default_factory=list, description="Evidence text spans")

class ThreatClassificationItemSchema(BaseModel):
    label: ThreatCategoryEnum = Field(..., description="Threat taxonomy category")
    confidence: float = Field(..., description="Confidence in classification (0.0 to 1.0)")
    is_primary: bool = Field(False, description="Whether this is the primary classification label")

class ThreatClassificationSchema(BaseModel):
    primary: ThreatCategoryEnum = Field(ThreatCategoryEnum.UNKNOWN, description="Primary threat label")
    secondary: List[ThreatCategoryEnum] = Field(default_factory=list, description="Secondary threat labels")
    confidence: float = Field(0.0, description="Overall classification confidence")

class ThreatRiskAssessmentSchema(BaseModel):
    level: ThreatRiskLevelEnum = Field(ThreatRiskLevelEnum.LOW, description="Overall risk level")
    score: int = Field(0, description="0-100 normalized risk score")
    confidence: float = Field(0.0, description="Confidence in risk assessment")

class Phase3ThreatAnalysisResponse(BaseModel):
    email_id: str = Field(..., description="Email ID")
    analysis: Dict[str, str] = Field(default_factory=lambda: {
        "engine_version": "3.0.0",
        "model_version": "deterministic-v1",
        "analyzed_at": datetime.utcnow().isoformat()
    })
    classification: ThreatClassificationSchema = Field(default_factory=ThreatClassificationSchema)
    risk: ThreatRiskAssessmentSchema = Field(default_factory=ThreatRiskAssessmentSchema)
    signals: List[ThreatSignalSchema] = Field(default_factory=list)
    evidence: List[ThreatEvidenceSpanSchema] = Field(default_factory=list)
    explanation: str = Field("", description="Explainable threat summary for security analyst")
    limitations: List[str] = Field(default_factory=lambda: [
        "Threat classification is an assessment, not proof of malicious intent.",
        "Phase 3 does not establish physical sender location or attacker identity."
    ])
