import re
from typing import List, Dict, Any, Optional
from app.schemas.canonical import CanonicalEmailObject

class URLFeatureExtractor:
    """
    Analyzes structural features of URLs extracted in Phase 1:
    - Hostname length & excessive subdomains
    - IP address hostnames
    - Credential/login path presence
    - Levenshtein lookalike domain detection against target domain/known brands
    """

    KNOWN_BRANDS = ["paypal", "microsoft", "google", "apple", "amazon", "bankofamerica", "wellsfargo", "chase"]

    @classmethod
    def extract_features(cls, canonical_email: CanonicalEmailObject) -> Dict[str, Any]:
        urls = canonical_email.indicators.urls
        from_domain = canonical_email.identity.from_[0].domain if canonical_email.identity.from_ else None

        has_ip_hostname = False
        has_credential_path = False
        has_lookalike_domain = False
        suspicious_urls: List[str] = []
        lookalike_domains: List[str] = []

        for u in urls:
            hostname = (u.hostname or "").lower()
            path = (u.path or "").lower()

            # IP Hostname check
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
                has_ip_hostname = True
                suspicious_urls.append(u.raw_url)

            # Credential path check
            if re.search(r"/(?:login|signin|auth|verify|account|password|update|reset)", path):
                has_credential_path = True

            # Lookalike domain check
            if hostname:
                is_lookalike, matched_brand = cls._check_lookalike(hostname, from_domain)
                if is_lookalike:
                    has_lookalike_domain = True
                    lookalike_domains.append(hostname)
                    suspicious_urls.append(u.raw_url)

        return {
            "url_count": len(urls),
            "has_ip_hostname": has_ip_hostname,
            "has_credential_path": has_credential_path,
            "has_lookalike_domain": has_lookalike_domain,
            "lookalike_domains": lookalike_domains,
            "suspicious_urls": list(set(suspicious_urls))
        }

    @classmethod
    def _check_lookalike(cls, hostname: str, from_domain: Optional[str]) -> tuple[bool, Optional[str]]:
        clean_host = hostname.rstrip(".").lower()
        parts = clean_host.split(".")
        if len(parts) < 2:
            return False, None

        registered_domain = parts[-2]

        for brand in cls.KNOWN_BRANDS:
            if registered_domain == brand:
                continue
            dist = cls.levenshtein_distance(registered_domain, brand)
            if 1 <= dist <= 2:
                return True, brand
            # Homoglyph character substitution check (e.g. paypa1 vs paypal)
            if brand in clean_host and registered_domain != brand:
                return True, brand

        if from_domain:
            clean_from = from_domain.split(".")[0].lower()
            if clean_from and len(clean_from) > 3 and registered_domain != clean_from:
                dist = cls.levenshtein_distance(registered_domain, clean_from)
                if 1 <= dist <= 2:
                    return True, clean_from

        return False, None

    @classmethod
    def levenshtein_distance(cls, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return cls.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
