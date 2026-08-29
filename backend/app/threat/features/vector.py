from typing import Dict, Any
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import Phase2ForensicAnalysisResponse
from app.threat.features.content import ContentFeatureExtractor
from app.threat.features.urls import URLFeatureExtractor
from app.threat.features.attachments import AttachmentFeatureExtractor

class FeatureVectorAggregator:
    """
    Aggregates extracted features across Phase 1 (normalized email), Phase 2 (forensics),
    and Phase 3 (content NLP, social engineering, URLs, attachments) into a unified Feature Vector dictionary.
    """

    @classmethod
    def aggregate(
        cls,
        canonical_email: CanonicalEmailObject,
        forensics: Phase2ForensicAnalysisResponse
    ) -> Dict[str, Any]:
        content_feats = ContentFeatureExtractor.extract_features(canonical_email)
        url_feats = URLFeatureExtractor.extract_features(canonical_email)
        att_feats = AttachmentFeatureExtractor.extract_features(canonical_email)

        # Phase 2 Forensic features
        auth = forensics.authentication
        headers = forensics.header_analysis

        spf_fail = auth.spf.result in ("FAIL", "SOFTFAIL", "PERMERROR")
        dkim_fail = auth.dkim.result in ("FAIL", "PERMERROR")
        dmarc_fail = auth.dmarc.result == "FAIL"

        from_reply_to_mismatch = not headers.from_reply_to.match and bool(headers.from_reply_to.domain_b)
        from_return_path_mismatch = not headers.from_return_path.match and bool(headers.from_return_path.domain_b)

        forensic_rule_ids = [f.rule_id for f in forensics.findings]

        return {
            "content": content_feats,
            "url": url_feats,
            "attachment": att_feats,
            "forensics": {
                "spf_fail": spf_fail,
                "dkim_fail": dkim_fail,
                "dmarc_fail": dmarc_fail,
                "from_reply_to_mismatch": from_reply_to_mismatch,
                "from_return_path_mismatch": from_return_path_mismatch,
                "forensic_rule_ids": forensic_rule_ids
            }
        }
