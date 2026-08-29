from typing import Optional
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import DomainComparisonSchema, HeaderAnalysisSchema
from app.forensics.authentication.alignment import DomainAlignmentAnalyzer

class HeaderComparisonAnalyzer:
    """
    Performs deterministic comparison of:
    - From domain vs Reply-To domain
    - From domain vs Return-Path domain
    - Message-ID domain vs From domain
    """

    @classmethod
    def analyze(cls, canonical_email: CanonicalEmailObject) -> HeaderAnalysisSchema:
        identity = canonical_email.identity

        from_domain = identity.from_[0].domain if identity.from_ else None
        reply_to_domain = identity.reply_to[0].domain if identity.reply_to else None
        
        return_path_domain = None
        if identity.return_path:
            clean_rp = identity.return_path.split("@")[-1].strip().lower().rstrip(">")
            return_path_domain = clean_rp

        # Message-ID domain
        msg_id_domain = cls.extract_message_id_domain(identity.message_id)

        # 1. From vs Reply-To
        from_reply_to = cls.compare_domains(
            from_domain,
            reply_to_domain,
            "Reply-To address is specified",
            "Reply-To domain differs from visible From address domain"
        )

        # 2. From vs Return-Path
        from_return_path = cls.compare_domains(
            from_domain,
            return_path_domain,
            "Return-Path envelope matches From domain",
            "Return-Path envelope domain differs from visible From address domain"
        )

        # 3. From vs Message-ID
        from_msg_id = cls.compare_domains(
            from_domain,
            msg_id_domain,
            "Message-ID domain matches visible From domain",
            "Message-ID domain differs from visible From address domain"
        )

        # Unique sender domains
        sender_domains = set()
        for d in [from_domain, reply_to_domain, return_path_domain, msg_id_domain]:
            if d:
                sender_domains.add(d.lower())

        return HeaderAnalysisSchema(
            from_reply_to=from_reply_to,
            from_return_path=from_return_path,
            message_id=from_msg_id,
            sender_domains=list(sender_domains)
        )

    @classmethod
    def compare_domains(
        cls,
        domain_a: Optional[str],
        domain_b: Optional[str],
        match_note: str,
        mismatch_note: str
    ) -> DomainComparisonSchema:
        if not domain_a or not domain_b:
            return DomainComparisonSchema(
                match=True,
                domain_a=domain_a,
                domain_b=domain_b,
                note="One or both domains absent; comparison skipped"
            )

        org_a = DomainAlignmentAnalyzer.get_organizational_domain(domain_a)
        org_b = DomainAlignmentAnalyzer.get_organizational_domain(domain_b)

        match = bool(org_a and org_b and org_a == org_b)

        return DomainComparisonSchema(
            match=match,
            domain_a=domain_a,
            domain_b=domain_b,
            note=match_note if match else mismatch_note
        )

    @classmethod
    def extract_message_id_domain(cls, message_id: Optional[str]) -> Optional[str]:
        if not message_id or "@" not in message_id:
            return None
        clean_id = message_id.strip().strip("<>").strip()
        if "@" in clean_id:
            return clean_id.split("@")[-1].strip().lower()
        return None
