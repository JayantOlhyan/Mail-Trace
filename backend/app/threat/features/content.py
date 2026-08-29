import re
from typing import List, Dict, Any, Optional
from app.schemas.canonical import CanonicalEmailObject

class ContentFeatureExtractor:
    """
    Extracts semantic and keyword content signals (urgency, credential harvesting prompts,
    financial requests, authority claims) with exact text span references.
    """

    URGENCY_PATTERNS = [
        r"\b(?:immediately|urgent|urgently|within \d+ hours|act now|final warning|account suspension|suspended|terminate|requires immediate)\b",
        r"\b(?:before today's deadline|action required|immediate action|verify now|at once|critical update)\b"
    ]

    CREDENTIAL_PATTERNS = [
        r"\b(?:password|passcode|otp|one time password|mfa|two factor|verify your account|login|sign in|update credentials|reset password|confirm identity)\b",
        r"\b(?:account verification|security confirmation|re-authenticate|unlock account|account restricted)\b"
    ]

    FINANCIAL_PATTERNS = [
        r"\b(?:wire transfer|payment|bank account|invoice|outstanding balance|transfer funds|new bank details|swift code|iban|gift card|payroll|remittance)\b",
        r"\b(?:update payment details|change bank account|deposit|billing update|account number change)\b"
    ]

    AUTHORITY_PATTERNS = [
        r"\b(?:ceo|chief executive officer|cfo|chief financial officer|cto|president|director|executive|head of hr|payroll department|helpdesk|security team|it administrator)\b"
    ]

    @classmethod
    def extract_features(cls, canonical_email: CanonicalEmailObject) -> Dict[str, Any]:
        from_str = " ".join([f"{a.display_name or ''} {a.address}" for a in canonical_email.identity.from_])
        text_content = f"{from_str}\n{canonical_email.content.subject}\n{canonical_email.content.text_body}"
        if canonical_email.content.html_body:
            text_content += f"\n{canonical_email.content.html_body}"

        text_lower = text_content.lower()

        urgency_spans = cls._find_spans(text_content, cls.URGENCY_PATTERNS)
        credential_spans = cls._find_spans(text_content, cls.CREDENTIAL_PATTERNS)
        financial_spans = cls._find_spans(text_content, cls.FINANCIAL_PATTERNS)
        authority_spans = cls._find_spans(text_content, cls.AUTHORITY_PATTERNS)

        return {
            "has_urgency": bool(urgency_spans),
            "urgency_score": min(1.0, len(urgency_spans) * 0.45) if urgency_spans else 0.0,
            "urgency_spans": urgency_spans,

            "has_credential_prompt": bool(credential_spans),
            "credential_score": min(1.0, len(credential_spans) * 0.50) if credential_spans else 0.0,
            "credential_spans": credential_spans,

            "has_financial_request": bool(financial_spans),
            "financial_score": min(1.0, len(financial_spans) * 0.40) if financial_spans else 0.0,
            "financial_spans": financial_spans,

            "has_authority_claim": bool(authority_spans),
            "authority_score": min(1.0, len(authority_spans) * 0.35) if authority_spans else 0.0,
            "authority_spans": authority_spans,
        }

    @classmethod
    def _find_spans(cls, text: str, patterns: List[str]) -> List[str]:
        spans: List[str] = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                span = m.group(0).strip()
                if span and span not in spans:
                    spans.append(span)
        return spans
