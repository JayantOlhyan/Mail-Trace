import uuid
from typing import List
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import TimelineEventSchema, RelayAnalysisSchema

class ForensicTimelineBuilder:
    """
    Builds a deterministic, chronological event timeline from available email header timestamps,
    Message-ID dates, and Received relay hops.
    """

    @classmethod
    def build_timeline(
        cls,
        canonical_email: CanonicalEmailObject,
        relay_analysis: RelayAnalysisSchema
    ) -> List[TimelineEventSchema]:
        events: List[TimelineEventSchema] = []

        # 1. Received Hops Events
        for hop in relay_analysis.hops:
            desc = f"SMTP Relay Hop #{hop.hop}"
            if hop.source_hostname or hop.source_ip:
                desc += f" from {hop.source_hostname or 'unknown'} ({hop.source_ip or 'unknown IP'})"
            if hop.destination:
                desc += f" to {hop.destination}"

            events.append(
                TimelineEventSchema(
                    event_id=f"TLE-{uuid.uuid4().hex[:8]}",
                    timestamp=hop.timestamp,
                    event_type="smtp_relay_hop",
                    description=desc,
                    evidence_reference=f"Received Header #{hop.hop}",
                    source="Received Header"
                )
            )

        # 2. Origin Date Header Event
        date_header = canonical_email.metadata.received_date or canonical_email.headers.raw.get("Date")
        if date_header:
            events.append(
                TimelineEventSchema(
                    event_id=f"TLE-{uuid.uuid4().hex[:8]}",
                    timestamp=date_header,
                    event_type="email_date_header",
                    description=f"Sender client claimed message creation time: {date_header}",
                    evidence_reference="Date Header",
                    source="Date Header"
                )
            )

        # 3. MailTrace Ingestion Event
        events.append(
            TimelineEventSchema(
                event_id=f"TLE-{uuid.uuid4().hex[:8]}",
                timestamp=canonical_email.metadata.parsed_at,
                event_type="evidence_ingestion",
                description=f"Evidence {canonical_email.evidence.evidence_id} ingested and parsed by MailTrace v{canonical_email.metadata.parser_version}",
                evidence_reference=canonical_email.evidence.sha256,
                source="MailTrace Engine"
            )
        )

        return events
