from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class EvidenceTable(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # EV-xxxxxx
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped[Optional["EmailTable"]] = relationship("EmailTable", back_populates="evidence", uselist=False)

class EmailTable(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), ForeignKey("evidence.id"), index=True, nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    subject: Mapped[str] = mapped_column(Text, default="", nullable=False)
    text_body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    html_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_headers_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    evidence: Mapped["EvidenceTable"] = relationship("EvidenceTable", back_populates="email")
    addresses: Mapped[List["EmailAddressTable"]] = relationship("EmailAddressTable", back_populates="email", cascade="all, delete-orphan")
    received_headers: Mapped[List["ReceivedHeaderTable"]] = relationship("ReceivedHeaderTable", back_populates="email", cascade="all, delete-orphan")
    urls: Mapped[List["URLTable"]] = relationship("URLTable", back_populates="email", cascade="all, delete-orphan")
    attachments: Mapped[List["AttachmentTable"]] = relationship("AttachmentTable", back_populates="email", cascade="all, delete-orphan")

    # Phase 2 Relationships
    authentication_results: Mapped[List["AuthenticationResultTable"]] = relationship("AuthenticationResultTable", back_populates="email", cascade="all, delete-orphan")
    forensic_findings: Mapped[List["ForensicFindingTable"]] = relationship("ForensicFindingTable", back_populates="email", cascade="all, delete-orphan")
    relay_hops: Mapped[List["RelayHopTable"]] = relationship("RelayHopTable", back_populates="email", cascade="all, delete-orphan")
    timeline_events: Mapped[List["ForensicTimelineEventTable"]] = relationship("ForensicTimelineEventTable", back_populates="email", cascade="all, delete-orphan")

    # Phase 3 Relationships
    threat_analyses: Mapped[List["ThreatAnalysisTable"]] = relationship("ThreatAnalysisTable", back_populates="email", cascade="all, delete-orphan")

    # Phase 4 Relationships
    infrastructure_indicators: Mapped[List["InfrastructureIndicatorTable"]] = relationship("InfrastructureIndicatorTable", back_populates="email", cascade="all, delete-orphan")

class EmailAddressTable(Base):
    __tablename__ = "email_addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # from, to, cc, bcc, reply_to, return_path

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="addresses")

class ReceivedHeaderTable(Base):
    __tablename__ = "received_headers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    hop_order: Mapped[int] = mapped_column(Integer, nullable=False)
    source_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_ip: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="received_headers")

class URLTable(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    raw_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    scheme: Mapped[str] = mapped_column(String(16), nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_context: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="urls")

class AttachmentTable(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # ATT-xxxxxx
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    content_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    disposition: Mapped[str] = mapped_column(String(32), default="attachment", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="attachments")

class AuthenticationResultTable(Base):
    __tablename__ = "authentication_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    mechanism: Mapped[str] = mapped_column(String(32), nullable=False)  # spf, dkim, dmarc, arc
    result: Mapped[str] = mapped_column(String(32), nullable=False)     # PASS, FAIL, SOFTFAIL, etc.
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    selector: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="authentication_results")

class ForensicFindingTable(Base):
    __tablename__ = "forensic_findings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # FND-xxxxxx
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    rule_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # HDR001-HDR010
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)  # info, low, medium, high, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Integer, nullable=False)  # Stored as float/int
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="forensic_findings")
    evidence_items: Mapped[List["FindingEvidenceTable"]] = relationship("FindingEvidenceTable", back_populates="finding", cascade="all, delete-orphan")

class FindingEvidenceTable(Base):
    __tablename__ = "finding_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    finding_id: Mapped[str] = mapped_column(String(64), ForeignKey("forensic_findings.id"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(128), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    finding: Mapped["ForensicFindingTable"] = relationship("ForensicFindingTable", back_populates="evidence_items")

class RelayHopTable(Base):
    __tablename__ = "relay_hops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    hop_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_ip: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="relay_hops")

class ForensicTimelineEventTable(Base):
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # TLE-xxxxxx
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="timeline_events")

# Phase 3 Tables
class ThreatAnalysisTable(Base):
    __tablename__ = "threat_analyses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # TAN-xxxxxx
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(32), default="3.0.0", nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), default="deterministic-v1", nullable=False)
    primary_class: Mapped[str] = mapped_column(String(64), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)     # 0-100
    classification_confidence: Mapped[float] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="threat_analyses")
    signals: Mapped[List["ThreatSignalTable"]] = relationship("ThreatSignalTable", back_populates="threat_analysis", cascade="all, delete-orphan")
    classifications: Mapped[List["ThreatClassificationTable"]] = relationship("ThreatClassificationTable", back_populates="threat_analysis", cascade="all, delete-orphan")

class ThreatSignalTable(Base):
    __tablename__ = "threat_signals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # SIG-xxxxxx
    analysis_id: Mapped[str] = mapped_column(String(64), ForeignKey("threat_analyses.id"), index=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_id: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)  # THR001-THR008
    severity: Mapped[str] = mapped_column(String(32), nullable=False)  # info, low, medium, high, critical
    score: Mapped[float] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    threat_analysis: Mapped["ThreatAnalysisTable"] = relationship("ThreatAnalysisTable", back_populates="signals")
    evidence_spans: Mapped[List["ThreatEvidenceTable"]] = relationship("ThreatEvidenceTable", back_populates="signal", cascade="all, delete-orphan")

class ThreatEvidenceTable(Base):
    __tablename__ = "threat_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signal_id: Mapped[str] = mapped_column(String(64), ForeignKey("threat_signals.id"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(128), nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    text_span: Mapped[str] = mapped_column(Text, nullable=False)
    raw_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    signal: Mapped["ThreatSignalTable"] = relationship("ThreatSignalTable", back_populates="evidence_spans")

class ThreatClassificationTable(Base):
    __tablename__ = "threat_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(String(64), ForeignKey("threat_analyses.id"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)

    threat_analysis: Mapped["ThreatAnalysisTable"] = relationship("ThreatAnalysisTable", back_populates="classifications")

# Phase 4 Tables
class InfrastructureIndicatorTable(Base):
    __tablename__ = "infrastructure_indicators"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # IND-xxxxxx
    email_id: Mapped[str] = mapped_column(String(64), ForeignKey("emails.id"), index=True, nullable=False)
    indicator_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # ip, domain, hostname, url
    indicator_value: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)  # received_header, from, reply_to
    priority: Mapped[str] = mapped_column(String(16), nullable=False)  # high, medium, low
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped["EmailTable"] = relationship("EmailTable", back_populates="infrastructure_indicators")
    ip_intelligence: Mapped[List["IPIntelligenceTable"]] = relationship("IPIntelligenceTable", back_populates="indicator", cascade="all, delete-orphan")
    domain_intelligence: Mapped[List["DomainIntelligenceTable"]] = relationship("DomainIntelligenceTable", back_populates="indicator", cascade="all, delete-orphan")
    reputation_results: Mapped[List["ReputationResultTable"]] = relationship("ReputationResultTable", back_populates="indicator", cascade="all, delete-orphan")

class IPIntelligenceTable(Base):
    __tablename__ = "ip_intelligence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_id: Mapped[str] = mapped_column(String(64), ForeignKey("infrastructure_indicators.id"), index=True, nullable=False)
    ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False)  # PUBLIC, PRIVATE, etc.
    asn: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    isp: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    network_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reverse_dns: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cloud: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    datacenter: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    vpn: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    tor: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    proxy: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    indicator: Mapped["InfrastructureIndicatorTable"] = relationship("InfrastructureIndicatorTable", back_populates="ip_intelligence")
    geolocation: Mapped[Optional["GeolocationResultTable"]] = relationship("GeolocationResultTable", back_populates="ip_intelligence", uselist=False, cascade="all, delete-orphan")

class GeolocationResultTable(Base):
    __tablename__ = "geolocation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip_intelligence_id: Mapped[int] = mapped_column(Integer, ForeignKey("ip_intelligence.id"), index=True, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    accuracy: Mapped[str] = mapped_column(String(32), default="approximate", nullable=False)
    confidence: Mapped[float] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    ip_intelligence: Mapped["IPIntelligenceTable"] = relationship("IPIntelligenceTable", back_populates="geolocation")

class DomainIntelligenceTable(Base):
    __tablename__ = "domain_intelligence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_id: Mapped[str] = mapped_column(String(64), ForeignKey("infrastructure_indicators.id"), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    registrar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at_date: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    expires_at_date: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    updated_at_date: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    domain_age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    privacy_protected: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    indicator: Mapped["InfrastructureIndicatorTable"] = relationship("InfrastructureIndicatorTable", back_populates="domain_intelligence")
    dns_records: Mapped[List["DNSRecordTable"]] = relationship("DNSRecordTable", back_populates="domain_intelligence", cascade="all, delete-orphan")

class DNSRecordTable(Base):
    __tablename__ = "dns_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_intelligence_id: Mapped[int] = mapped_column(Integer, ForeignKey("domain_intelligence.id"), index=True, nullable=False)
    record_type: Mapped[str] = mapped_column(String(16), nullable=False)  # A, AAAA, MX, NS, CNAME, TXT
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    ttl: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    domain_intelligence: Mapped["DomainIntelligenceTable"] = relationship("DomainIntelligenceTable", back_populates="dns_records")

class ReputationResultTable(Base):
    __tablename__ = "reputation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_id: Mapped[str] = mapped_column(String(64), ForeignKey("infrastructure_indicators.id"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # CLEAN, SUSPICIOUS, MALICIOUS, UNKNOWN
    score: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Integer, nullable=False)
    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    indicator: Mapped["InfrastructureIndicatorTable"] = relationship("InfrastructureIndicatorTable", back_populates="reputation_results")

class EnrichmentLookupTable(Base):
    __tablename__ = "enrichment_lookups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    indicator_value: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
