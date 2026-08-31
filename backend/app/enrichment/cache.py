import time
from typing import Dict, Any, Optional

class IntelligenceCache:
    """
    In-memory TTL-based Intelligence Cache abstraction for ThreatTrace AI.
    Decoupled interface allows zero-code transition to Redis or memcached.
    """

    _store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._store:
            entry = cls._store[key]
            if time.time() < entry["expires_at"]:
                return entry["value"]
            else:
                del cls._store[key]
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        cls._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }

    @classmethod
    def delete(cls, key: str) -> None:
        cls._store.pop(key, None)

    @classmethod
    def clear(cls) -> None:
        cls._store.clear()
