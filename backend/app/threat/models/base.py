from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.threat import ThreatClassificationSchema

class ThreatModel(ABC):
    """
    Abstract base class for ThreatTrace AI Threat Classification Models.
    Allows swapping between baseline deterministic engine, local ML models, and LLM providers.
    """

    @abstractmethod
    def predict(self, feature_vector: Dict[str, Any]) -> ThreatClassificationSchema:
        """Classifies the email based on the aggregated feature vector."""
        pass
