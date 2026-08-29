from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.ingestion.validator import IngestionValidationError
from app.ingestion.eml_ingestor import EmlIngestionPipeline
from app.schemas.canonical import CanonicalEmailObject, HeadersSchema, IndicatorsSchema, AttachmentSchema
from app.models.db import EmailTable, EvidenceTable
from app.parsing.email_parser import EmailParserEngine
import os

router = APIRouter(prefix="/emails", tags=["Emails"])

@router.post(
    "/upload",
    response_model=CanonicalEmailObject,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Parse Raw .EML Evidence File"
)
async def upload_email(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts raw .eml file upload, validates payload size and readability,
    computes SHA-256 evidence hash, safely stores raw file, parses MIME headers/body/attachments,
    persists metadata to PostgreSQL, and returns canonical normalized email object.
    """
    try:
        content = await file.read()
        filename = file.filename or "uploaded_email.eml"
        canonical = await EmlIngestionPipeline.process_upload(content, filename, db)
        return canonical
    except IngestionValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if "exceeds" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to ingest email: {str(e)}")

@router.get(
    "/{email_id}",
    response_model=CanonicalEmailObject,
    summary="Get Normalized Email Object by ID"
)
async def get_email(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    email_record = await db.get(EmailTable, email_id)
    if not email_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email ID '{email_id}' not found")

    evidence_record = await db.get(EvidenceTable, email_record.evidence_id)
    if not evidence_record or not os.path.exists(evidence_record.storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original evidence file missing from storage")

    with open(evidence_record.storage_path, "rb") as f:
        raw_bytes = f.read()

    canonical_obj, _ = EmailParserEngine.parse_eml(raw_bytes, evidence_record.id, evidence_record.filename)
    return canonical_obj

@router.get(
    "/{email_id}/headers",
    response_model=HeadersSchema,
    summary="Get Email Raw and Structured Headers"
)
async def get_email_headers(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    canonical = await get_email(email_id, db)
    return canonical.headers

@router.get(
    "/{email_id}/indicators",
    response_model=IndicatorsSchema,
    summary="Get Extracted Indicators (IPs, Domains, URLs, Email Addresses)"
)
async def get_email_indicators(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    canonical = await get_email(email_id, db)
    return canonical.indicators

@router.get(
    "/{email_id}/attachments",
    response_model=list[AttachmentSchema],
    summary="Get Email Attachment Metadata List"
)
async def get_email_attachments(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    canonical = await get_email(email_id, db)
    return canonical.attachments
