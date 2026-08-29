import ipaddress
from typing import List, Optional
from app.parsing.models import ParsedEmail, ReceivedHop
from app.forensics.models import HopAnalysisResult

class HopAnalyzer:
    """
    SMTP Relay Path & Origin Tracing Engine for MailTrace.
    Analyzes Received header chains to identify the Observed Origin IP (earliest reliable public IP)
    and flags routing anomalies while stripping internal/private network hops.
    """

    @classmethod
    def analyze(cls, parsed_email: ParsedEmail) -> HopAnalysisResult:
        hops = parsed_email.headers.received_chain
        anomalies: List[str] = []
        observed_origin_ip: Optional[str] = None
        untrusted_hops_count = 0

        if not hops:
            return HopAnalysisResult(
                observed_origin_ip=None,
                probable_origin_infrastructure="No SMTP Hop Headers Available",
                total_hops=0,
                untrusted_hops_count=0,
                relay_anomalies=["No Received headers found in message payload"]
            )

        # Iterate hops starting from earliest (index 1) to newest
        for hop in hops:
            if not hop.ip_address:
                continue

            if cls._is_public_ip(hop.ip_address):
                untrusted_hops_count += 1
                if not observed_origin_ip:
                    observed_origin_ip = hop.ip_address

        # Check for relay path anomalies
        if untrusted_hops_count == 0:
            anomalies.append("All observed SMTP hops were internal/private IP addresses; no public origin IP detected")
        elif untrusted_hops_count > 4:
            anomalies.append(f"Excessive untrusted public relays detected ({untrusted_hops_count} public hops)")

        # Timestamp sequence check
        if len(hops) > 1:
            missing_timestamps = sum(1 for h in hops if not h.timestamp_raw)
            if missing_timestamps > 0:
                anomalies.append(f"{missing_timestamps} relay hop(s) missing timestamp metadata")

        infrastructure_label = f"Observed Public IP {observed_origin_ip}" if observed_origin_ip else "Internal Relay Network"

        return HopAnalysisResult(
            observed_origin_ip=observed_origin_ip,
            probable_origin_infrastructure=infrastructure_label,
            total_hops=len(hops),
            untrusted_hops_count=untrusted_hops_count,
            relay_anomalies=anomalies
        )

    @classmethod
    def _is_public_ip(cls, ip_str: str) -> bool:
        """Returns True if ip_str is a valid, globally routable public IP address."""
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            return not (
                ip_obj.is_private or
                ip_obj.is_loopback or
                ip_obj.is_link_local or
                ip_obj.is_multicast or
                ip_obj.is_unspecified
            )
        except ValueError:
            return False
