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


def _parse_encoded_ip(ip_str: str):
    try:
        return ipaddress.ip_address(ip_str)
    except ValueError:
        pass
    
    # Try integer parsing
    try:
        if ip_str.startswith("0x") or ip_str.startswith("0X"):
            return ipaddress.ip_address(int(ip_str, 16))
        elif ip_str.startswith("0") and len(ip_str) > 1 and ip_str.isdigit():
            return ipaddress.ip_address(int(ip_str, 8))
        elif ip_str.isdigit():
            return ipaddress.ip_address(int(ip_str))
    except ValueError:
        pass

    # Try dot notation with hex/octal parts
    parts = ip_str.split('.')
    if len(parts) == 4:
        try:
            parsed_parts = []
            for p in parts:
                if p.startswith('0x') or p.startswith('0X'):
                    parsed_parts.append(int(p, 16))
                elif p.startswith('0') and len(p) > 1:
                    parsed_parts.append(int(p, 8))
                else:
                    parsed_parts.append(int(p))
            return ipaddress.ip_address(f"{parsed_parts[0]}.{parsed_parts[1]}.{parsed_parts[2]}.{parsed_parts[3]}")
        except:
            pass
            
    return None

def is_ip_private_or_restricted(ip_str: str) -> bool:
    """
    Checks whether an IP address belongs to a private, loopback, or restricted network block.
    """
    ip_obj = _parse_encoded_ip(ip_str)
    if ip_obj is None:
        return False
        
    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
        return True
    for net in BLOCKED_NETWORKS:
        if ip_obj in net:
            return True
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

        hostname_lower = urllib.parse.unquote(hostname).lower()
        if hostname_lower in BLOCKED_HOSTNAMES:
            return False, f"Forbidden target hostname: '{hostname}' (Restricted Internal Host)."

        # Try to parse encoded IPs first
        if _parse_encoded_ip(hostname_lower) is not None:
            if is_ip_private_or_restricted(hostname_lower):
                return False, f"Forbidden destination IP: '{hostname}' (Internal/Private Network Block)."
        else:
            # If it's not directly parsable as IP, resolve it
            import socket
            try:
                resolved_ip = socket.gethostbyname(hostname_lower)
            except socket.gaierror:
                resolved_ip = hostname_lower

            if is_ip_private_or_restricted(resolved_ip) or is_ip_private_or_restricted(hostname_lower):
                return False, f"Forbidden destination IP: '{hostname}' (Internal/Private Network Block)."

        return True, "URL validated successfully."
    except Exception as e:
        return False, f"URL validation error: {str(e)}"
