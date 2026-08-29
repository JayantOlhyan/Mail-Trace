import re
from typing import Dict, List, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import DKIMAnalysisSchema, AuthResultStatus

class DKIMAnalyzer:
    """
    Parses DKIM-Signature and DKIM results from email authentication headers.
    Extracts signing domain (d=), selector (s=), algorithm (a=), canonicalization (c=), signed headers (h=), body hash (bh=).
    """

    @classmethod
    def analyze(cls, canonical_email: CanonicalEmailObject) -> DKIMAnalysisSchema:
        auth_headers = canonical_email.headers.authentication_headers
        raw_headers = canonical_email.headers.raw

        # 1. Parse DKIM-Signature header if present
        dkim_sig = raw_headers.get("DKIM-Signature") or raw_headers.get("dkim-signature") or auth_headers.get("DKIM-Signature")
        
        status = AuthResultStatus.NONE
        signing_domain = None
        selector = None
        algorithm = None
        canonicalization = None
        signed_headers: List[str] = []
        body_hash = None
        signature_present = False

        if dkim_sig:
            signature_present = True
            params = cls._parse_signature_params(dkim_sig)
            signing_domain = params.get("d")
            selector = params.get("s")
            algorithm = params.get("a")
            canonicalization = params.get("c")
            body_hash = params.get("bh")
            if params.get("h"):
                signed_headers = [h.strip() for h in params["h"].split(":")]

        # 2. Inspect Authentication-Results header for DKIM verdict
        auth_res = auth_headers.get("Authentication-Results") or raw_headers.get("Authentication-Results")
        if auth_res:
            res_status, res_domain, res_selector = cls._parse_auth_results_dkim(auth_res)
            if res_status != AuthResultStatus.NONE:
                status = res_status
            if not signing_domain and res_domain:
                signing_domain = res_domain
            if not selector and res_selector:
                selector = res_selector

        # If DKIM signature present but no header status, default to PASS (signature present observation)
        if signature_present and status == AuthResultStatus.NONE:
            status = AuthResultStatus.PASS

        return DKIMAnalysisSchema(
            result=status,
            signing_domain=signing_domain,
            selector=selector,
            algorithm=algorithm,
            canonicalization=canonicalization,
            signed_headers=signed_headers,
            body_hash=body_hash,
            signature_present=signature_present,
            source_header="DKIM-Signature" if signature_present else "Authentication-Results",
            raw_evidence=dkim_sig or auth_res
        )

    @classmethod
    def _parse_signature_params(cls, header: str) -> Dict[str, str]:
        params = {}
        tokens = re.split(r";(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", header)
        for token in tokens:
            if "=" in token:
                k, v = token.split("=", 1)
                params[k.strip().lower()] = v.strip().strip('"')
        return params

    @classmethod
    def _parse_auth_results_dkim(cls, header: str) -> tuple[AuthResultStatus, Optional[str], Optional[str]]:
        status = AuthResultStatus.NONE
        domain = None
        selector = None

        m_dkim = re.search(r"dkim=(pass|fail|neutral|none|permerror|temperror)", header, re.IGNORECASE)
        if m_dkim:
            raw = m_dkim.group(1).upper()
            if "PASS" in raw:
                status = AuthResultStatus.PASS
            elif "FAIL" in raw:
                status = AuthResultStatus.FAIL
            elif "PERMERROR" in raw:
                status = AuthResultStatus.PERMERROR
            elif "TEMPERROR" in raw:
                status = AuthResultStatus.TEMPERROR
            else:
                status = AuthResultStatus.NEUTRAL

        m_domain = re.search(r"header\.d=([^\s;]+)", header, re.IGNORECASE)
        if m_domain:
            domain = m_domain.group(1).strip()

        m_selector = re.search(r"header\.s=([^\s;]+)", header, re.IGNORECASE)
        if m_selector:
            selector = m_selector.group(1).strip()

        return status, domain, selector
