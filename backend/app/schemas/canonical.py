from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EvidenceRef(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence tracking identifier (EV-xxxxxx)")
    filename: str = Field(..., description="Original filename of uploaded .eml file")
    sha256: str = Field(..., description="SHA-256 cryptographic hash of exact raw bytes")
    size_bytes: int = Field(..., description="Exact file size in bytes")

class AddressObject(BaseModel):
    display_name: Optional[str] = Field(None, description="Formatted display name")
    address: str = Field(..., description="Clean lowercase email address")
    domain: str = Field(..., description="Extracted domain part of email address")

class IdentitySchema(BaseModel):
    message_id: Optional[str] = Field(None, description="Unique Message-ID header")
    from_: List[AddressObject] = Field(default_factory=list, alias="from", description="From address(es)")
    to: List[AddressObject] = Field(default_factory=list, description="To recipient(s)")
    cc: List[AddressObject] = Field(default_factory=list, description="Cc recipient(s)")
    bcc: List[AddressObject] = Field(default_factory=list, description="Bcc recipient(s)")
    reply_to: List[AddressObject] = Field(default_factory=list, description="Reply-To address(es)")
    return_path: Optional[str] = Field(None, description="Return-Path envelope sender address")

    model_config = ConfigDict(populate_by_name=True)

class ContentSchema(BaseModel):
    subject: str = Field("(No Subject)", description="Decoded email subject line")
    text_body: str = Field("", description="Extracted plain text body content")
    html_body: Optional[str] = Field(None, description="Extracted raw HTML body content")

class ReceivedHopSchema(BaseModel):
    hop_order: int = Field(..., description="1-indexed sequence order of SMTP relay hop")
    raw_value: str = Field(..., description="Original unparsed Received header string")
    source_hostname: Optional[str] = Field(None, description="Extracted sending hostname")
    source_ip: Optional[str] = Field(None, description="Extracted sending IP address")
    destination: Optional[str] = Field(None, description="Extracted receiving hostname/IP")
    protocol: Optional[str] = Field(None, description="SMTP transfer protocol used")
    timestamp: Optional[str] = Field(None, description="Parsed ISO timestamp if available")

class HeadersSchema(BaseModel):
    raw: Dict[str, str] = Field(default_factory=dict, description="Complete raw headers dictionary")
    received: List[ReceivedHopSchema] = Field(default_factory=list, description="Structured Received hop chain")
    authentication_headers: Dict[str, str] = Field(default_factory=dict, description="Authentication headers (SPF/DKIM/DMARC/ARC)")
    other: Dict[str, str] = Field(default_factory=dict, description="Custom X-headers and unclassified headers")

class IPIndicator(BaseModel):
    ip: str = Field(..., description="IPv4 or IPv6 address string")
    ip_version: str = Field(..., description="IPv4 or IPv6")
    category: str = Field(..., description="public, private, loopback, reserved, unspecified")
    source_context: str = Field(..., description="Provenance location (e.g. Received Header #1, Text Body)")

class DomainIndicator(BaseModel):
    domain: str = Field(..., description="Normalized domain string")
    source_context: str = Field(..., description="Provenance location (e.g. From Header, URL hostname)")

class URLIndicator(BaseModel):
    raw_url: str = Field(..., description="Original extracted URL string")
    normalized_url: str = Field(..., description="Normalized URL string")
    scheme: str = Field(..., description="http or https or mailto")
    hostname: Optional[str] = Field(None, description="Target hostname")
    port: Optional[int] = Field(None, description="URL port if explicit")
    path: Optional[str] = Field(None, description="URL path component")
    source_context: str = Field(..., description="Provenance location (e.g. HTML Body, Text Body)")

class EmailAddressIndicator(BaseModel):
    address: str = Field(..., description="Clean email address string")
    source_context: str = Field(..., description="Provenance location (e.g. Body text, Cc Header)")

class IndicatorsSchema(BaseModel):
    ips: List[IPIndicator] = Field(default_factory=list, description="Extracted IP address indicators")
    domains: List[DomainIndicator] = Field(default_factory=list, description="Extracted domain indicators")
    urls: List[URLIndicator] = Field(default_factory=list, description="Extracted URL indicators")
    email_addresses: List[EmailAddressIndicator] = Field(default_factory=list, description="Extracted email address indicators")

class AttachmentSchema(BaseModel):
    attachment_id: str = Field(..., description="Unique attachment identifier (ATT-xxxxxx)")
    filename: str = Field(..., description="Original attachment filename (sanitized)")
    mime_type: str = Field(..., description="MIME content type")
    size_bytes: int = Field(..., description="Attachment payload size in bytes")
    content_id: Optional[str] = Field(None, description="Inline Content-ID if present")
    disposition: str = Field("attachment", description="attachment or inline")
    sha256: str = Field(..., description="SHA-256 cryptographic hash of attachment bytes")

class MetadataSchema(BaseModel):
    received_date: Optional[str] = Field(None, description="Email Date header timestamp")
    parsed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO UTC parsing timestamp")
    parser_version: str = Field("1.0.0", description="MailTrace parser version")

class CanonicalEmailObject(BaseModel):
    email_id: str = Field(..., description="Unique identifier for parsed email")
    evidence: EvidenceRef = Field(..., description="Immutable raw evidence metadata")
    identity: IdentitySchema = Field(..., description="Sender and recipient identities")
    content: ContentSchema = Field(..., description="Text and HTML body contents")
    headers: HeadersSchema = Field(..., description="Raw and structured headers")
    indicators: IndicatorsSchema = Field(..., description="Extracted IOC indicators")
    attachments: List[AttachmentSchema] = Field(default_factory=list, description="Attachment metadata list")
    metadata: MetadataSchema = Field(default_factory=MetadataSchema, description="Parsing metadata")
