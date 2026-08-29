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

