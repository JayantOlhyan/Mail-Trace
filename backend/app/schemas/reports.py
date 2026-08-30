from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class EvidenceItemSchema(BaseModel):
    id: str = Field(description="Unique evidence item identifier, e.g. EVD-001")
    evidence_type: str = Field(description="Type of evidence: Raw Email, Header, SPF, DKIM, IP, etc.")
    source: str = Field(description="Source module or header line")
    captured_at: str = Field(description="Timestamp when evidence was captured")
    origin_phase: str = Field(description="Originating pipeline phase (Phase 1 to Phase 6)")
    sha256_hash: str = Field(description="SHA-256 cryptographic hash of evidence content")
    case_id: Optional[str] = Field(default=None, description="Associated case ID")


class ChainOfCustodyItemSchema(BaseModel):
    id: int
    evidence_id: str
    action: str = Field(description="Action performed: Captured, Normalized, Analyzed, Correlated, Added to Case, Included in Report")
    timestamp: str
    actor: str = Field(description="System or analyst who performed the action")
    details: Optional[str] = None


class ManifestFileEntrySchema(BaseModel):
    name: str = Field(description="Filename in evidence package")
    sha256: str = Field(description="SHA-256 checksum of the file")
    size_bytes: int


class EvidencePackageManifestSchema(BaseModel):
    case_id: str
    report_id: str
    generated_at: str
    evidence_count: int
    files: List[ManifestFileEntrySchema]


class ThreatFindingReportSchema(BaseModel):
    id: str
    finding: str
    category: str
    severity: str
    evidence_reference: str
    originating_phase: str


class MachineFindingsSchema(BaseModel):
    ai_classification: str
    risk_score: int
    confidence: str
    spf_status: str
    dkim_status: str
    dmarc_status: str
    detected_indicators: List[str]
    origin_ip: Optional[str] = None
    origin_asn: Optional[str] = None
    origin_location: Optional[str] = None
    infrastructure_clusters: List[str] = []
    campaign_candidates: List[str] = []


class AnalystFindingsSchema(BaseModel):
    analyst_classification: Optional[str] = Field(default=None, description="Analyst confirmed classification")
    analyst_confidence: Optional[str] = None
    case_status: str
    assigned_analyst: str
    analyst_notes: List[Dict[str, Any]] = []
    analyst_decision: Optional[str] = None
    recommended_actions: List[str] = []


class ForensicReportSchema(BaseModel):
    report_id: str = Field(description="Unique report identifier, e.g. RPT-2026-0042")
    case_id: str
    version: str = "1.0"
    generated_at: str
    generated_by: str = "MailTrace Forensic Engine"
    investigation_id: str
    evidence_count: int

    # Core Content Sections
    executive_summary: str
    machine_findings: MachineFindingsSchema
    analyst_findings: AnalystFindingsSchema
    threat_findings: List[ThreatFindingReportSchema]
    
    # Detailed Technical Evidence
    email_metadata: Dict[str, Any]
    header_forensics: Dict[str, Any]
    relay_path: List[Dict[str, Any]]
    infrastructure_intelligence: Dict[str, Any]
    indicators_of_compromise: List[Dict[str, Any]]
    graph_summary: Dict[str, Any]
    campaign_analysis: Optional[Dict[str, Any]] = None
    timeline_events: List[Dict[str, Any]] = []
    evidence_inventory: List[EvidenceItemSchema] = []
    chain_of_custody: List[ChainOfCustodyItemSchema] = []

    limitations_statement: str = (
        "This report combines machine-generated forensic evidence with analyst findings. "
        "Observed infrastructure (IPs, ASNs, geolocations) reflects technical network routing "
        "and does not establish legal attribution or physical identity."
    )
