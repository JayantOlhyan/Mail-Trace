from typing import Dict, Any

class CommonInfrastructureSuppression:
    """
    Suppresses false-positive campaign correlations caused by ubiquitous shared infrastructure
    (AWS, Cloudflare, Google Cloud, Microsoft Azure, Akamai, Google DNS, Cloudflare DNS).
    """

    COMMON_ASNS = {"AS13335", "AS16509", "AS15169", "AS8075", "AS20940", "AS14618"}
    COMMON_ORGS = {
        "cloudflare, inc.", "amazon.com, inc.", "google llc",
        "microsoft corporation", "akamai technologies", "fastly"
    }
    COMMON_NAMESERVERS = {
        "ns1.cloudflare.com", "ns2.cloudflare.com",
        "ns-1.awsdns.com", "ns-2.awsdns.com"
    }

    @classmethod
    def get_suppression_penalty(cls, entity_type: str, canonical_value: str, metadata: Dict[str, Any]) -> float:
        """
        Returns a suppression multiplier between 0.0 (fully suppressed common infra)
        and 1.0 (unique attacker-controlled infra).
        """
        clean_val = canonical_value.lower()

        # Check ASN / Organization
        asn = str(metadata.get("asn", "")).upper()
        org = str(metadata.get("organization", "")).lower()

        if asn in cls.COMMON_ASNS or any(co in org for co in cls.COMMON_ORGS):
            return 0.15  # 85% suppression penalty for common cloud providers

        if entity_type == "NAMESERVER" and clean_val in cls.COMMON_NAMESERVERS:
            return 0.10  # 90% suppression penalty for shared public CDNs/DNS

        # Common public mail relays (Gmail, Outlook)
        if entity_type == "MAIL_SERVER" and any(m in clean_val for m in ["google.com", "outlook.com", "protection.outlook.com"]):
            return 0.20  # 80% suppression penalty

        return 1.0  # Full correlation weight for custom/dedicated infrastructure
