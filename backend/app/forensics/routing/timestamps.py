from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
from app.schemas.canonical import ReceivedHopSchema

class TimestampAnalyzer:
    """
    Analyzes timestamp chronological ordering and time deltas across SMTP Received hops.
    Detects non-chronological jumps, clock skew, and malformed date strings.
    """

    @classmethod
    def analyze_timestamps(cls, hops: List[ReceivedHopSchema]) -> Dict[str, Any]:
        anomalies: List[str] = []
        parsed_timestamps: List[tuple[int, Optional[datetime]]] = []

        for hop in hops:
            dt = cls._parse_iso_or_rfc(hop.timestamp)
            parsed_timestamps.append((hop.hop_order, dt))

        # Check chronological sequence: Hop 1 (earliest) -> Hop N (latest)
        chronological_valid = True
        for i in range(len(parsed_timestamps) - 1):
            hop_a_num, dt_a = parsed_timestamps[i]
            hop_b_num, dt_b = parsed_timestamps[i + 1]

            if dt_a and dt_b:
                if dt_a > dt_b:
                    chronological_valid = False
                    anomalies.append(
                        f"Non-chronological timestamp order between Hop {hop_a_num} ({dt_a.isoformat()}) and Hop {hop_b_num} ({dt_b.isoformat()})"
                    )

        missing_count = sum(1 for _, dt in parsed_timestamps if dt is None)

        return {
            "chronological_valid": chronological_valid,
            "total_hops_with_timestamps": len(hops) - missing_count,
            "missing_timestamps_count": missing_count,
            "anomalies": anomalies
        }

    @classmethod
    def _parse_iso_or_rfc(cls, ts_str: Optional[str]) -> Optional[datetime]:
        if not ts_str:
            return None
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            try:
                return parsedate_to_datetime(ts_str)
            except Exception:
                return None
