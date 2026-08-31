import ipaddress
import urllib.parse
from typing import Tuple


BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private IPv4
    ipaddress.ip_network("172.16.0.0/12"),    # Private IPv4
    ipaddress.ip_network("192.168.0.0/16"),   # Private IPv4
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("::1/128"),          # Loopback IPv6
    ipaddress.ip_network("fc00::/7"),         # Unique local IPv6
    ipaddress.ip_network("fe80::/10"),        # Link-local IPv6
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "169.254.169.254",
    "instance-data",
}


def is_ip_private_or_restricted(ip_str: str) -> bool:
    """
    Checks whether an IP address belongs to a private, loopback, or restricted network block.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
            return True
        for net in BLOCKED_NETWORKS:
            if ip_obj in net:
                return True
        return False
    except ValueError:
        return False


def validate_url_for_ssrf(url: str) -> Tuple[bool, str]:
    """
    Validates a target URL against SSRF vulnerabilities.
    Returns (is_safe: bool, reason: str).
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, f"Forbidden URL scheme: '{parsed.scheme}'. Only HTTP/HTTPS allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: Missing hostname."

        hostname_lower = hostname.lower()
        if hostname_lower in BLOCKED_HOSTNAMES:
            return False, f"Forbidden target hostname: '{hostname}' (Restricted Internal Host)."

        # If hostname is an IP string, validate directly
        if is_ip_private_or_restricted(hostname_lower):
            return False, f"Forbidden destination IP: '{hostname}' (Internal/Private Network Block)."

        return True, "URL validated successfully."
    except Exception as e:
        return False, f"URL validation error: {str(e)}"
