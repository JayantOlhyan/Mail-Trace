import re
from typing import Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import DMARCAnalysisSchema, AuthResultStatus, DMARCPolicyEnum
from app.forensics.authentication.alignment import DomainAlignmentAnalyzer

class DMARCAnalyzer:
    """
    Evaluates DMARC compliance from Authentication-Results headers and checks SPF/DKIM alignment with From domain.
    """

    @classmethod
    def analyze(
        cls,
        canonical_email: CanonicalEmailObject,
        spf_domain: Optional[str],
        dkim_domain: Optional[str]
    ) -> DMARCAnalysisSchema:
        auth_headers = canonical_email.headers.authentication_headers
        raw_headers = canonical_email.headers.raw

        from_domain = canonical_email.identity.from_[0].domain if canonical_email.identity.from_ else None

        # Check alignment
        alignment = DomainAlignmentAnalyzer.evaluate_alignment(from_domain, spf_domain, dkim_domain)
        spf_aligned = alignment.spf_aligned_relaxed
        dkim_aligned = alignment.dkim_aligned_relaxed

        status = AuthResultStatus.NONE
        policy = DMARCPolicyEnum.ABSENT
        evaluated_domain = from_domain

        auth_res = auth_headers.get("Authentication-Results") or raw_headers.get("Authentication-Results")
        if auth_res:
            res_status, res_policy, res_domain = cls._parse_auth_results_dmarc(auth_res)
            if res_status != AuthResultStatus.NONE:
                status = res_status
            if res_policy != DMARCPolicyEnum.ABSENT:
                policy = res_policy
            if res_domain:
                evaluated_domain = res_domain

        # If DMARC header explicit result absent, infer from alignment
        if status == AuthResultStatus.NONE:
            if spf_aligned or dkim_aligned:
                status = AuthResultStatus.PASS
            elif from_domain:
                status = AuthResultStatus.FAIL

        return DMARCAnalysisSchema(
            result=status,
            header_from_domain=from_domain,
            evaluated_domain=evaluated_domain,
            policy=policy,
            spf_aligned=spf_aligned,
            dkim_aligned=dkim_aligned,
            raw_evidence=auth_res
        )

    @classmethod
    def _parse_auth_results_dmarc(cls, header: str) -> tuple[AuthResultStatus, DMARCPolicyEnum, Optional[str]]:
        status = AuthResultStatus.NONE
        policy = DMARCPolicyEnum.ABSENT
        domain = None

        m_dmarc = re.search(r"dmarc=(pass|fail|none|temperror|permerror)", header, re.IGNORECASE)
        if m_dmarc:
            raw = m_dmarc.group(1).upper()
            if "PASS" in raw:
                status = AuthResultStatus.PASS
            elif "FAIL" in raw:
                status = AuthResultStatus.FAIL
            else:
                status = AuthResultStatus.NONE

        m_policy = re.search(r"action=(reject|quarantine|none)|p=(reject|quarantine|none)", header, re.IGNORECASE)
        if m_policy:
            raw_p = (m_policy.group(1) or m_policy.group(2)).lower()
            if raw_p == "reject":
                policy = DMARCPolicyEnum.REJECT
            elif raw_p == "quarantine":
                policy = DMARCPolicyEnum.QUARANTINE
            elif raw_p == "none":
                policy = DMARCPolicyEnum.NONE

        m_domain = re.search(r"header\.from=([^\s;]+)", header, re.IGNORECASE)
        if m_domain:
            domain = m_domain.group(1).strip()

        return status, policy, domain
