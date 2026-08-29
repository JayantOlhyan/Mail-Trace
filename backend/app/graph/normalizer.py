import re
import ipaddress
from typing import Tuple

class EntityNormalizer:
    """
    Entity Normalization & Canonicalization for MailTrace Investigation Graph.
    Ensures identical entities observed across different emails resolve to a single canonical node.
    """

    @classmethod
    def normalize_domain(cls, domain_str: str) -> Tuple[str, str]:
        if not domain_str:
            return "", ""
        clean = domain_str.strip().lower().rstrip(".")
        display = domain_str.strip().rstrip(".")
        return clean, display

    @classmethod
    def normalize_ip(cls, ip_str: str) -> Tuple[str, str]:
        if not ip_str:
            return "", ""
        clean_str = ip_str.strip()
        try:
            ip_obj = ipaddress.ip_address(clean_str)
            canonical = str(ip_obj)
            return canonical, canonical
        except ValueError:
            return clean_str, clean_str

    @classmethod
    def normalize_url(cls, url_str: str) -> Tuple[str, str]:
        if not url_str:
            return "", ""
        clean = url_str.strip()
        # Remove trailing slashes and query string for canonical value
        canonical = re.sub(r"/+$", "", clean.split("?")[0].lower())
        return canonical, clean

    @classmethod
    def normalize_email_address(cls, email_str: str) -> Tuple[str, str]:
        if not email_str:
            return "", ""
        clean = email_str.strip().lower()
        return clean, email_str.strip()
