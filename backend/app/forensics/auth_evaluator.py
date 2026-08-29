import re
from typing import List, Optional
from app.schemas.canonical import CanonicalEmailObject
from app.forensics.models import (
    AuthenticationVerdict,
    SPFResult,
    DKIMResult,
    DMARCResult,
    SpoofingAnalysis,
    AuthStatus,
    DMARCPolicy,
)

class AuthEvaluator:
    """
    Email Forensics & Authentication Evaluation Engine for MailTrace.
    Evaluates SPF, DKIM, DMARC alignment, Display Name Spoofing, and Envelope Sender Mismatches.
    """

    KNOWN_EXECUTIVE_TITLES = [
        "ceo", "chief executive officer", "cfo", "chief financial officer",
        "cto", "president", "director", "founder", "payroll", "human resources", "hr manager"
    ]

    @classmethod
    def evaluate(cls, parsed_email: CanonicalEmailObject) -> AuthenticationVerdict:
        from_address = parsed_email.identity.from_[0].address if parsed_email.identity.from_ else ""
        from_domain = parsed_email.identity.from_[0].domain if parsed_email.identity.from_ else ""

        # 1. Evaluate SPF
        spf_result = cls._evaluate_spf(parsed_email, from_domain)

        # 2. Evaluate DKIM
        dkim_result = cls._evaluate_dkim(parsed_email, from_domain)

        # 3. Evaluate DMARC (Alignment of SPF/DKIM with From header domain)
        dmarc_result = cls._evaluate_dmarc(parsed_email, from_domain, spf_result, dkim_result)

        # 4. Evaluate Spoofing (Display name, Reply-To, Return-Path)
        spoofing_result = cls._evaluate_spoofing(parsed_email, from_domain)

        # 5. Compute overall Auth Risk Score & Fully Authenticated state
        is_authenticated = (
            spf_result.status == AuthStatus.PASS and
            dkim_result.status == AuthStatus.PASS and
            dmarc_result.status == AuthStatus.PASS and
            not spoofing_result.is_reply_to_mismatched and
            not spoofing_result.is_display_name_spoofed
        )

        auth_risk_score = cls._calculate_auth_risk(spf_result, dkim_result, dmarc_result, spoofing_result)

        return AuthenticationVerdict(
            spf=spf_result,
            dkim=dkim_result,
            dmarc=dmarc_result,
            spoofing=spoofing_result,
            is_fully_authenticated=is_authenticated,
            overall_auth_risk_score=auth_risk_score
        )

    @classmethod
    def _extract_domain(cls, email_address: str) -> str:
        if not email_address or "@" not in email_address:
            return ""
        return email_address.split("@")[-1].lower().strip()

    @classmethod
    def _evaluate_spf(cls, parsed_email: CanonicalEmailObject, from_domain: str) -> SPFResult:
        auth_headers = parsed_email.headers.authentication_headers
        auth_results = " ".join([f"{k}: {v}" for k, v in auth_headers.items()]).lower()

        if "spf=pass" in auth_results:
            return SPFResult(status=AuthStatus.PASS, domain=from_domain, reason="SPF pass confirmed in headers")
        elif "spf=fail" in auth_results or "spf=softfail" in auth_results:
            status = AuthStatus.FAIL if "spf=fail" in auth_results else AuthStatus.SOFTFAIL
            return SPFResult(status=status, domain=from_domain, reason="SPF failure indicated in relay headers")

        if parsed_email.identity.return_path:
            return_domain = cls._extract_domain(parsed_email.identity.return_path)
            if return_domain and return_domain == from_domain:
                return SPFResult(status=AuthStatus.PASS, domain=from_domain, reason="Return-Path domain aligns with From domain")
            elif return_domain and return_domain != from_domain:
                return SPFResult(status=AuthStatus.SOFTFAIL, domain=from_domain, reason=f"Return-Path domain ({return_domain}) differs from From domain ({from_domain})")

        return SPFResult(status=AuthStatus.NONE, domain=from_domain, reason="No SPF evaluation record available")

    @classmethod
    def _evaluate_dkim(cls, parsed_email: CanonicalEmailObject, from_domain: str) -> DKIMResult:
        auth_headers = parsed_email.headers.authentication_headers
        dkim_sig = auth_headers.get("DKIM-Signature") or auth_headers.get("Dkim-Signature")
        auth_results = " ".join([f"{k}: {v}" for k, v in auth_headers.items()]).lower()

        if not dkim_sig and "dkim=pass" not in auth_results:
            return DKIMResult(status=AuthStatus.NONE, signature_present=False, reason="No DKIM-Signature header present")

        if "dkim=pass" in auth_results:
            return DKIMResult(status=AuthStatus.PASS, domain=from_domain, signature_present=True, reason="DKIM signature verified")
        elif "dkim=fail" in auth_results:
            return DKIMResult(status=AuthStatus.FAIL, domain=from_domain, signature_present=True, reason="DKIM signature verification failed")

        return DKIMResult(status=AuthStatus.PASS, domain=from_domain, signature_present=True, reason="DKIM signature present")

    @classmethod
    def _evaluate_dmarc(cls, parsed_email: CanonicalEmailObject, from_domain: str, spf: SPFResult, dkim: DKIMResult) -> DMARCResult:
        align_spf = (spf.status == AuthStatus.PASS and spf.domain == from_domain)
        align_dkim = (dkim.status == AuthStatus.PASS and dkim.domain == from_domain)

        auth_headers = parsed_email.headers.authentication_headers
        auth_results = " ".join([f"{k}: {v}" for k, v in auth_headers.items()]).lower()

        policy = DMARCPolicy.NONE
        if "dmarc=action=reject" in auth_results or "p=reject" in auth_results:
            policy = DMARCPolicy.REJECT
        elif "dmarc=action=quarantine" in auth_results or "p=quarantine" in auth_results:
            policy = DMARCPolicy.QUARANTINE

        if align_spf or align_dkim or "dmarc=pass" in auth_results:
            return DMARCResult(
                status=AuthStatus.PASS,
                policy=policy,
                align_spf=align_spf,
                align_dkim=align_dkim,
                reason="DMARC alignment satisfied via SPF or DKIM"
            )

        return DMARCResult(
            status=AuthStatus.FAIL,
            policy=policy,
            align_spf=align_spf,
            align_dkim=align_dkim,
            reason="DMARC alignment failed: Neither SPF nor DKIM passed aligned with From domain"
        )

    @classmethod
    def _evaluate_spoofing(cls, parsed_email: CanonicalEmailObject, from_domain: str) -> SpoofingAnalysis:
        reasons: List[str] = []
        is_display_name_spoofed = False
        is_reply_to_mismatched = False
        is_return_path_mismatched = False
        impersonated_name = None

        from_name = parsed_email.identity.from_[0].display_name if parsed_email.identity.from_ else ""
        reply_to = parsed_email.identity.reply_to[0].address if parsed_email.identity.reply_to else None
        return_path = parsed_email.identity.return_path

        # 1. Executive / Title Display Name Spoofing Check
        from_name_lower = (from_name or "").lower()
        for title in cls.KNOWN_EXECUTIVE_TITLES:
            if title in from_name_lower:
                is_display_name_spoofed = True
                impersonated_name = from_name
                reasons.append(f"Display name contains sensitive executive/role title '{title}' ('{from_name}')")
                break

        # 2. Reply-To Mismatch Check
        if reply_to:
            reply_to_domain = cls._extract_domain(reply_to)
            if reply_to_domain and reply_to_domain != from_domain:
                is_reply_to_mismatched = True
                reasons.append(f"Reply-To address domain ({reply_to_domain}) differs from From address domain ({from_domain})")

        # 3. Return-Path Mismatch Check
        if return_path:
            return_domain = cls._extract_domain(return_path)
            if return_domain and return_domain != from_domain:
                is_return_path_mismatched = True
                reasons.append(f"Return-Path envelope domain ({return_domain}) differs from From address domain ({from_domain})")

        return SpoofingAnalysis(
            is_display_name_spoofed=is_display_name_spoofed,
            is_reply_to_mismatched=is_reply_to_mismatched,
            is_return_path_mismatched=is_return_path_mismatched,
            impersonated_name=impersonated_name,
            reasons=reasons
        )

    @classmethod
    def _calculate_auth_risk(cls, spf: SPFResult, dkim: DKIMResult, dmarc: DMARCResult, spoof: SpoofingAnalysis) -> int:
        score = 0
        if spf.status in (AuthStatus.FAIL, AuthStatus.SOFTFAIL):
            score += 25
        if dkim.status == AuthStatus.FAIL:
            score += 20
        if dmarc.status == AuthStatus.FAIL:
            score += 30
        if spoof.is_display_name_spoofed:
            score += 35
        if spoof.is_reply_to_mismatched:
            score += 40
        if spoof.is_return_path_mismatched:
            score += 15
        return min(100, score)
