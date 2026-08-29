from typing import List
from app.schemas.canonical import CanonicalEmailObject
from app.schemas.forensics import RelayAnalysisSchema, RelayHopAnalysisSchema
from app.forensics.routing.timestamps import TimestampAnalyzer

class ReceivedRoutingAnalyzer:
    """
    Reconstructs relay chain hops and performs structural routing anomaly analysis.
    """

    @classmethod
    def analyze(cls, canonical_email: CanonicalEmailObject) -> RelayAnalysisSchema:
        raw_hops = canonical_email.headers.received

        analyzed_hops: List[RelayHopAnalysisSchema] = []
        anomalies: List[str] = []

        for hop in raw_hops:
            analyzed_hops.append(
                RelayHopAnalysisSchema(
                    hop=hop.hop_order,
                    source_hostname=hop.source_hostname,
                    source_ip=hop.source_ip,
                    destination=hop.destination,
                    protocol=hop.protocol,
                    timestamp=hop.timestamp,
                    raw_value=hop.raw_value
                )
            )

        # Run timestamp sequence analysis
        ts_analysis = TimestampAnalyzer.analyze_timestamps(raw_hops)
        if ts_analysis["anomalies"]:
            anomalies.extend(ts_analysis["anomalies"])

        if len(raw_hops) == 0:
            anomalies.append("No Received headers present in email payload")

        return RelayAnalysisSchema(
            hops=analyzed_hops,
            timestamp_analysis=ts_analysis,
            anomalies=anomalies
        )
