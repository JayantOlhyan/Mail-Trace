import re
from typing import Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import ARCAnalysisSchema, AuthResultStatus

class ARCAnalyzer:
    """
    Extracts Authenticated Received Chain (ARC) evidence headers:
    ARC-Seal, ARC-Message-Signature, ARC-Authentication-Results.
    """

    @classmethod
    def analyze(cls, canonical_email: CanonicalEmailObject) -> ARCAnalysisSchema:
        raw_headers = canonical_email.headers.raw

        arc_seal = raw_headers.get("ARC-Seal") or raw_headers.get("arc-seal")
        arc_msg_sig = raw_headers.get("ARC-Message-Signature") or raw_headers.get("arc-message-signature")
        arc_auth_res = raw_headers.get("ARC-Authentication-Results") or raw_headers.get("arc-authentication-results")

        present = bool(arc_seal or arc_msg_sig or arc_auth_res)
        result: Optional[AuthResultStatus] = None

        if arc_seal:
            m_cv = re.search(r"cv=(pass|fail|none)", arc_seal, re.IGNORECASE)
            if m_cv:
                cv = m_cv.group(1).upper()
                if cv == "PASS":
                    result = AuthResultStatus.PASS
                elif cv == "FAIL":
                    result = AuthResultStatus.FAIL
                else:
                    result = AuthResultStatus.NONE
            else:
                result = AuthResultStatus.PASS if present else None

        raw_evidence = None
        if present:
            raw_evidence = f"ARC-Seal: {arc_seal or 'N/A'}; ARC-Auth: {arc_auth_res or 'N/A'}"

        return ARCAnalysisSchema(
            present=present,
            result=result,
            seal_present=bool(arc_seal),
            signature_present=bool(arc_msg_sig),
            raw_evidence=raw_evidence
        )
