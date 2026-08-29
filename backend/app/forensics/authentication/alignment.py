from typing import Optional
from app.schemas.forensics import AlignmentSchema

class DomainAlignmentAnalyzer:
    """
    Evaluates strict (exact FQDN match) vs relaxed (organizational domain match) alignment
    between the RFC 5322 visible From domain and SPF / DKIM evaluated domains.
    """

    @classmethod
    def get_organizational_domain(cls, domain: Optional[str]) -> Optional[str]:
        if not domain:
            return None
        clean_domain = domain.strip().lower().rstrip(".")
        parts = clean_domain.split(".")
        if len(parts) <= 2:
            return clean_domain
        # Basic TLD handling (e.g. co.uk, com.au, corp.example.com)
        if len(parts[-2]) <= 3 and len(parts[-1]) <= 2:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])

    @classmethod
    def evaluate_alignment(
        cls,
        header_from_domain: Optional[str],
        spf_domain: Optional[str],
        dkim_domain: Optional[str]
    ) -> AlignmentSchema:
        clean_from = header_from_domain.strip().lower().rstrip(".") if header_from_domain else ""
        clean_spf = spf_domain.strip().lower().rstrip(".") if spf_domain else ""
        clean_dkim = dkim_domain.strip().lower().rstrip(".") if dkim_domain else ""

        org_from = cls.get_organizational_domain(clean_from)
        org_spf = cls.get_organizational_domain(clean_spf)
        org_dkim = cls.get_organizational_domain(clean_dkim)

        spf_strict = bool(clean_from and clean_spf and clean_from == clean_spf)
        spf_relaxed = bool(org_from and org_spf and org_from == org_spf)

        dkim_strict = bool(clean_from and clean_dkim and clean_from == clean_dkim)
        dkim_relaxed = bool(org_from and org_dkim and org_from == org_dkim)

        return AlignmentSchema(
            spf_aligned_strict=spf_strict,
            spf_aligned_relaxed=spf_relaxed,
            dkim_aligned_strict=dkim_strict,
            dkim_aligned_relaxed=dkim_relaxed
        )
