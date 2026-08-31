from typing import Dict, Any, List
from app.schemas.threat import ThreatClassificationSchema, ThreatCategoryEnum
from app.threat.models.base import ThreatModel

class DeterministicThreatModel(ThreatModel):
    """
    Baseline deterministic model provider for ThreatTrace AI.
    Provides fast, reproducible, network-independent classification based on feature weights & rules.
    """

    def predict(self, feature_vector: Dict[str, Any]) -> ThreatClassificationSchema:
        content = feature_vector.get("content", {})
        urls = feature_vector.get("url", {})
        attachments = feature_vector.get("attachment", {})
        forensics = feature_vector.get("forensics", {})

        primary = ThreatCategoryEnum.LEGITIMATE
        secondary: List[ThreatCategoryEnum] = []
        confidence = 0.85

        has_urgency = content.get("has_urgency", False)
        has_credentials = content.get("has_credential_prompt", False)
        has_financial = content.get("has_financial_request", False)
        has_authority = content.get("has_authority_claim", False)

        has_lookalike = urls.get("has_lookalike_domain", False)
        has_cred_path = urls.get("has_credential_path", False)
        has_exec_att = attachments.get("has_executable", False)
        has_double_ext = attachments.get("has_double_extension", False)

        spf_fail = forensics.get("spf_fail", False)
        dkim_fail = forensics.get("dkim_fail", False)
        reply_mismatch = forensics.get("from_reply_to_mismatch", False)

        # 1. BEC Classification
        if (has_financial and has_authority) or (has_financial and reply_mismatch):
            primary = ThreatCategoryEnum.BUSINESS_EMAIL_COMPROMISE
            if has_financial:
                secondary.append(ThreatCategoryEnum.FINANCIAL_FRAUD)
            if reply_mismatch or spf_fail:
                secondary.append(ThreatCategoryEnum.IMPERSONATION)
            confidence = 0.94

        # 2. Credential Harvesting
        elif (has_credentials and has_cred_path) or (has_credentials and has_lookalike):
            primary = ThreatCategoryEnum.CREDENTIAL_HARVESTING
            secondary.append(ThreatCategoryEnum.PHISHING)
            confidence = 0.96

        # 3. Phishing
        elif has_lookalike or (has_urgency and has_credentials) or (has_credentials and reply_mismatch):
            primary = ThreatCategoryEnum.PHISHING
            if has_credentials:
                secondary.append(ThreatCategoryEnum.CREDENTIAL_HARVESTING)
            confidence = 0.91

        # 4. Malicious Delivery
        elif has_exec_att or has_double_ext:
            primary = ThreatCategoryEnum.MALICIOUS_DELIVERY
            confidence = 0.95

        # 5. Financial Fraud
        elif has_financial and has_urgency:
            primary = ThreatCategoryEnum.FINANCIAL_FRAUD
            secondary.append(ThreatCategoryEnum.SUSPICIOUS)
            confidence = 0.90

        # 6. Impersonation
        elif has_authority and (reply_mismatch or spf_fail):
            primary = ThreatCategoryEnum.IMPERSONATION
            secondary.append(ThreatCategoryEnum.SUSPICIOUS)
            confidence = 0.88

        # 7. Suspicious
        elif reply_mismatch or spf_fail or dkim_fail or has_urgency:
            primary = ThreatCategoryEnum.SUSPICIOUS
            confidence = 0.80

        return ThreatClassificationSchema(
            primary=primary,
            secondary=list(set(secondary)),
            confidence=confidence
        )
