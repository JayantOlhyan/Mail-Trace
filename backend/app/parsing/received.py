import re
import email
from typing import List
from dateutil import parser as date_parser
from app.schemas.canonical import ReceivedHopSchema

class ReceivedParser:
    """
    Parses SMTP Received headers into structured ReceivedHopSchema objects.
    Extracts source_hostname, source_ip, destination, protocol, and timestamp
    while preserving original hop order.
    """

    IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|\[(?:[a-fA-F0-9:]+)\]')
    FROM_REGEX = re.compile(r'from\s+([^\s]+)', re.IGNORECASE)
    BY_REGEX = re.compile(r'by\s+([^\s]+)', re.IGNORECASE)
    WITH_REGEX = re.compile(r'with\s+([^\s;]+)', re.IGNORECASE)

    @classmethod
    def parse_received_headers(cls, msg: email.message.EmailMessage) -> List[ReceivedHopSchema]:
        raw_received_list = msg.get_all("Received", [])
        if not raw_received_list:
            return []

        # Received headers in email byte stream appear newest-first (top of header list).
        # Reverse the list so hop_order 1 represents the earliest sending hop.
        reversed_list = list(reversed(raw_received_list))
        hops: List[ReceivedHopSchema] = []

        for idx, raw_val in enumerate(reversed_list, start=1):
            val_str = HeaderParser_decode(str(raw_val))
            
            # Extract IP
            ip_match = cls.IP_REGEX.search(val_str)
            source_ip = ip_match.group(0).strip("[]") if ip_match else None

            # Extract Hostnames
            from_match = cls.FROM_REGEX.search(val_str)
            by_match = cls.BY_REGEX.search(val_str)

            source_hostname = from_match.group(1).rstrip(";") if from_match else None
            destination = by_match.group(1).rstrip(";") if by_match else None

            # Extract Protocol
            with_match = cls.WITH_REGEX.search(val_str)
            protocol = with_match.group(1).rstrip(";") if with_match else None

            # Extract Timestamp
            timestamp_str = None
            if ";" in val_str:
                raw_time = val_str.split(";")[-1].strip()
                try:
                    dt = date_parser.parse(raw_time)
                    timestamp_str = dt.isoformat()
                except Exception:
                    timestamp_str = raw_time

            hops.append(ReceivedHopSchema(
                hop_order=idx,
                raw_value=val_str,
                source_hostname=source_hostname,
                source_ip=source_ip,
                destination=destination,
                protocol=protocol,
                timestamp=timestamp_str
            ))

        return hops

def HeaderParser_decode(text: str) -> str:
    from app.parsing.headers import HeaderParser
    return HeaderParser.decode_header_text(text)
