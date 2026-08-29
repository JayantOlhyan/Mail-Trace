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
