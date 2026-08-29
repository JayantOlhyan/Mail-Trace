import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Set, Tuple
from app.schemas.canonical import (
    IPIndicator,
    DomainIndicator,
    URLIndicator,
    EmailAddressIndicator,
    IndicatorsSchema,
    IdentitySchema,
    ReceivedHopSchema,
)
from app.parsing.headers import HeaderParser

class IndicatorExtractor:
    """
    Extracts URLs, Domains, IPs (IPv4 & IPv6 classified), and Email Addresses from text, HTML, and headers.
    Records provenance context for every extracted indicator without making external network calls.
    """

    URL_REGEX = re.compile(
        r'https?://[^\s<>"]+|www\.[^\s<>"]+|mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    IP_REGEX = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|'
        r'\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b|\b(?:[a-fA-F0-9]{1,4}:){1,7}:|::(?:[a-fA-F0-9]{1,4}:){0,6}[a-fA-F0-9]{1,4}\b',
        re.IGNORECASE
    )
    EMAIL_REGEX = re.compile(
        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        re.IGNORECASE
    )

    @classmethod
    def extract_all(
        cls,
        identity: IdentitySchema,
        received_hops: List[ReceivedHopSchema],
        text_body: str,
        html_body: str,
        raw_headers: dict
    ) -> IndicatorsSchema:

        ip_list: List[IPIndicator] = []
        domain_set: Set[Tuple[str, str]] = set()  # (domain, provenance)
        url_list: List[URLIndicator] = []
        email_list: List[EmailAddressIndicator] = []

        seen_ips: Set[str] = set()
        seen_urls: Set[str] = set()
        seen_emails: Set[str] = set()

        # 1. Process Received Hops IPs & Hostnames
        for hop in received_hops:
            if hop.source_ip and hop.source_ip not in seen_ips:
                cat, ip_ver = cls.classify_ip(hop.source_ip)
                ip_list.append(IPIndicator(
                    ip=hop.source_ip,
                    ip_version=ip_ver,
                    category=cat,
                    source_context=f"Received Header #{hop.hop_order}"
                ))
                seen_ips.add(hop.source_ip)

            if hop.source_hostname and "." in hop.source_hostname:
                domain_set.add((hop.source_hostname.lower().rstrip("."), f"Received Header #{hop.hop_order}"))

        # 2. Process Identities (From, To, Cc, Reply-To, Return-Path)
        all_identities = [
            ("From Header", identity.from_),
            ("To Header", identity.to),
            ("Cc Header", identity.cc),
            ("Bcc Header", identity.bcc),
            ("Reply-To Header", identity.reply_to),
        ]

        for context_name, addr_objs in all_identities:
            for obj in addr_objs:
                if obj.address and obj.address not in seen_emails:
                    email_list.append(EmailAddressIndicator(address=obj.address, source_context=context_name))
                    seen_emails.add(obj.address)
                if obj.domain:
                    domain_set.add((obj.domain.lower(), context_name))

        if identity.return_path:
            rp_obj = HeaderParser.parse_single_address(identity.return_path)
            if rp_obj.address and rp_obj.address not in seen_emails:
                email_list.append(EmailAddressIndicator(address=rp_obj.address, source_context="Return-Path Header"))
                seen_emails.add(rp_obj.address)
            if rp_obj.domain:
                domain_set.add((rp_obj.domain.lower(), "Return-Path Header"))

        # 3. Process Text & HTML Body
        for body_content, context_label in [(text_body, "Text Body"), (html_body or "", "HTML Body")]:
            if not body_content:
                continue

            # Extract URLs
            for raw_url in cls.URL_REGEX.findall(body_content):
                clean_url = raw_url.rstrip(".,;)'\"<>")
                if clean_url not in seen_urls:
                    parsed_url = cls._parse_url(clean_url, context_label)
                    url_list.append(parsed_url)
                    seen_urls.add(clean_url)

                    if parsed_url.hostname and "." in parsed_url.hostname:
                        domain_set.add((parsed_url.hostname.lower(), context_label))

            # Extract IPs in Body
            for raw_ip in cls.IP_REGEX.findall(body_content):
                clean_ip = raw_ip.strip("[]")
                if clean_ip not in seen_ips:
                    cat, ip_ver = cls.classify_ip(clean_ip)
                    if cat != "invalid":
                        ip_list.append(IPIndicator(
                            ip=clean_ip,
                            ip_version=ip_ver,
                            category=cat,
                            source_context=context_label
                        ))
                        seen_ips.add(clean_ip)

            # Extract Emails in Body
            for raw_email in cls.EMAIL_REGEX.findall(body_content):
                clean_email = raw_email.lower()
                if clean_email not in seen_emails:
                    email_list.append(EmailAddressIndicator(address=clean_email, source_context=context_label))
                    seen_emails.add(clean_email)
                    domain = clean_email.split("@")[-1]
                    domain_set.add((domain, context_label))

        domain_indicators = [
            DomainIndicator(domain=dom, source_context=ctx)
            for dom, ctx in domain_set if dom and "." in dom
        ]

        return IndicatorsSchema(
            ips=ip_list,
            domains=domain_indicators,
            urls=url_list,
            email_addresses=email_list
        )

    @classmethod
    def classify_ip(cls, ip_str: str) -> Tuple[str, str]:
        """Classifies IP address into IPv4/IPv6 and public/private/loopback/reserved/unspecified."""
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            version = f"IPv{ip_obj.version}"

            if ip_obj.is_loopback:
                cat = "loopback"
            elif ip_obj.is_private:
                cat = "private"
            elif ip_obj.is_multicast:
                cat = "reserved"
            elif ip_obj.is_reserved:
                cat = "reserved"
            elif ip_obj.is_unspecified:
                cat = "unspecified"
            else:
                cat = "public"

            return cat, version
        except ValueError:
            return "invalid", "unknown"

    @classmethod
    def _parse_url(cls, raw_url: str, source_context: str) -> URLIndicator:
        url_str = raw_url.strip()
        if not url_str.startswith("http://") and not url_str.startswith("https://") and not url_str.startswith("mailto:"):
            url_str = "http://" + url_str

        parsed = urlparse(url_str)
        scheme = parsed.scheme.lower() if parsed.scheme else "http"
        hostname = parsed.hostname.lower() if parsed.hostname else None
        port = parsed.port
        path = parsed.path if parsed.path else "/"
        if parsed.query:
            path += "?" + parsed.query

        return URLIndicator(
            raw_url=raw_url,
            normalized_url=url_str,
            scheme=scheme,
            hostname=hostname,
            port=port,
            path=path,
            source_context=source_context
        )
