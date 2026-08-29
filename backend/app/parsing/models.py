from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AttachmentMetadata(BaseModel):
    filename: str = Field(..., description="Name of the attachment file")
    content_type: str = Field(..., description="MIME content type of attachment")
    size_bytes: int = Field(..., description="Size of attachment in bytes")
    sha256_hash: str = Field(..., description="SHA-256 hash of attachment payload")
    content_disposition: Optional[str] = Field(None, description="Inline vs attachment disposition")

class BodyContent(BaseModel):
    plain_text: str = Field("", description="Extracted plain text body")
    html_raw: Optional[str] = Field(None, description="Original un-sanitized HTML body")
    html_sanitized: Optional[str] = Field(None, description="Sanitized HTML safe for workstation display")
    extracted_urls: List[str] = Field(default_factory=list, description="All URLs extracted from email body")

class ReceivedHop(BaseModel):
    hop_index: int = Field(..., description="1-indexed sequence order of SMTP hop")
    by_host: Optional[str] = Field(None, description="Receiving mail server hostname/IP")
    from_host: Optional[str] = Field(None, description="Claimed sending mail server hostname/IP")
    ip_address: Optional[str] = Field(None, description="Extracted IP address of sending hop")
    timestamp_raw: Optional[str] = Field(None, description="Raw timestamp string from Received header")

class HeaderData(BaseModel):
    from_address: str = Field(..., description="Extracted email address from From header")
    from_name: Optional[str] = Field(None, description="Display name from From header")
    to_addresses: List[str] = Field(default_factory=list, description="Recipient email addresses")
    cc_addresses: List[str] = Field(default_factory=list, description="CC email addresses")
    subject: str = Field("(No Subject)", description="Email Subject")
    date_raw: Optional[str] = Field(None, description="Raw Date header text")
    message_id: Optional[str] = Field(None, description="Unique Message-ID header")
    reply_to: Optional[str] = Field(None, description="Reply-To header address")
    return_path: Optional[str] = Field(None, description="Return-Path envelope sender address")
    received_chain: List[ReceivedHop] = Field(default_factory=list, description="Parsed Received header hop chain")
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="All custom and extra headers")

class ParsedEmail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email_id: str = Field(..., description="Unique UUID or SHA-256 derived email identifier")
    headers: HeaderData = Field(..., description="Structured header metadata")
    body: BodyContent = Field(..., description="Extracted plain and sanitized HTML body")
    attachments: List[AttachmentMetadata] = Field(default_factory=list, description="Parsed attachment metadata")
    raw_eml_size: int = Field(..., description="Total size of raw .eml payload in bytes")
    sha256_hash: str = Field(..., description="SHA-256 hash of entire raw .eml file")
    parsed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Parsing timestamp UTC")
