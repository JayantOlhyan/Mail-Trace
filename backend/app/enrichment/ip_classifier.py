import ipaddress
from app.enrichment.schemas import IPClassificationEnum

class IPClassifier:
    """
    Classifies IPv4 and IPv6 addresses into standard network categories.
    Prevents sending private, loopback, link-local, multicast, or reserved addresses
    to external intelligence providers.
    """

    @classmethod
    def classify(cls, ip_str: str) -> IPClassificationEnum:
        if not ip_str or not isinstance(ip_str, str):
            return IPClassificationEnum.INVALID

        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
        except ValueError:
            return IPClassificationEnum.INVALID

        if ip_obj.is_loopback:
            return IPClassificationEnum.LOOPBACK
        if ip_obj.is_link_local:
            return IPClassificationEnum.LINK_LOCAL
        if ip_obj.is_private:
            return IPClassificationEnum.PRIVATE
        if ip_obj.is_multicast:
            return IPClassificationEnum.MULTICAST
        if ip_obj.is_reserved:
            return IPClassificationEnum.RESERVED

        if ip_obj.is_global:
            return IPClassificationEnum.PUBLIC

        return IPClassificationEnum.RESERVED

    @classmethod
    def is_enrichable_public_ip(cls, ip_str: str) -> bool:
        return cls.classify(ip_str) == IPClassificationEnum.PUBLIC
