import re
from typing import Dict, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import SPFAnalysisSchema, AuthResultStatus

class SPFAnalyzer:
    """
    Extracts and evaluates SPF results from email authentication headers (Authentication-Results, Received-SPF).
    Does NOT perform live DNS queries.
    """

    @classmethod
    def analyze(cls, canonical_email: CanonicalEmailObject) -> SPFAnalysisSchema:
        auth_headers = canonical_email.headers.authentication_headers
        raw_headers = canonical_email.headers.raw

        # 1. Inspect Received-SPF header
        received_spf = raw_headers.get("Received-SPF") or raw_headers.get("received-spf")
        if received_spf:
            status, domain, client_ip = cls._parse_received_spf(received_spf)
            if status != AuthResultStatus.NONE:
                return SPFAnalysisSchema(
                    result=status,
                    domain=domain,
                    client_ip=client_ip,
                    evaluating_server=None,
                    source_header="Received-SPF",
                    raw_evidence=received_spf
                )

        # 2. Inspect Authentication-Results header
        auth_res = auth_headers.get("Authentication-Results") or auth_headers.get("authentication-results") or raw_headers.get("Authentication-Results")
        if auth_res:
            status, domain, client_ip, server = cls._parse_auth_results_spf(auth_res)
            if status != AuthResultStatus.NONE:
                return SPFAnalysisSchema(
                    result=status,
                    domain=domain,
                    client_ip=client_ip,
                    evaluating_server=server,
                    source_header="Authentication-Results",
                    raw_evidence=auth_res
                )

        return SPFAnalysisSchema(
            result=AuthResultStatus.NONE,
            domain=None,
            client_ip=None,
            evaluating_server=None,
            source_header="None",
            raw_evidence=None
        )

    @classmethod
    def _map_status(cls, raw_status: str) -> AuthResultStatus:
        s = raw_status.upper()
        if "PASS" in s:
            return AuthResultStatus.PASS
        elif "SOFTFAIL" in s:
            return AuthResultStatus.SOFTFAIL
        elif "FAIL" in s:
            return AuthResultStatus.FAIL
        elif "NEUTRAL" in s:
            return AuthResultStatus.NEUTRAL
        elif "PERMERROR" in s:
            return AuthResultStatus.PERMERROR
        elif "TEMPERROR" in s:
            return AuthResultStatus.TEMPERROR
        return AuthResultStatus.NONE

    @classmethod
    def _parse_received_spf(cls, header: str) -> tuple[AuthResultStatus, Optional[str], Optional[str]]:
        status = AuthResultStatus.NONE
        domain = None
        client_ip = None

        m_status = re.search(r"^(pass|fail|softfail|neutral|none|permerror|temperror)", header, re.IGNORECASE)
        if m_status:
            status = cls._map_status(m_status.group(1))

        m_domain = re.search(r"domain\s+of\s+([^\s;]+)", header, re.IGNORECASE) or re.search(r"identity=([^\s;]+)", header, re.IGNORECASE)
        if m_domain:
            val = m_domain.group(1).strip()
            domain = val.split("@")[-1] if "@" in val else val

        m_ip = re.search(r"client-ip=([0-9a-fA-F:\.]+)", header, re.IGNORECASE)
        if m_ip:
            client_ip = m_ip.group(1).strip()

        return status, domain, client_ip

    @classmethod
    def _parse_auth_results_spf(cls, header: str) -> tuple[AuthResultStatus, Optional[str], Optional[str], Optional[str]]:
        status = AuthResultStatus.NONE
        domain = None
        client_ip = None
        server = None

        parts = header.split(";")
        if parts:
            server = parts[0].split()[0] if parts[0].strip() else None

        m_spf = re.search(r"spf=(pass|fail|softfail|neutral|none|permerror|temperror)", header, re.IGNORECASE)
        if m_spf:
            status = cls._map_status(m_spf.group(1))

        m_domain = re.search(r"header\.from=([^\s;]+)", header, re.IGNORECASE) or re.search(r"smtp\.mailfrom=([^\s;]+)", header, re.IGNORECASE)
        if m_domain:
            val = m_domain.group(1).strip()
            domain = val.split("@")[-1] if "@" in val else val

        m_ip = re.search(r"smtp\.client-ip=([0-9a-fA-F:\.]+)", header, re.IGNORECASE)
        if m_ip:
            client_ip = m_ip.group(1).strip()

        return status, domain, client_ip, server
