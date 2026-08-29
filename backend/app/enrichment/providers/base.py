from abc import ABC, abstractmethod
from typing import Optional
from app.enrichment.schemas import (
    IPIntelligenceSchema,
    DomainIntelligenceSchema,
    ReputationIntelligenceSchema,
)

class IPIntelligenceProvider(ABC):
    @abstractmethod
    async def lookup_ip(self, ip: str) -> Optional[IPIntelligenceSchema]:
        pass

    @abstractmethod
    def provider_name(self) -> str:
        pass

class DomainIntelligenceProvider(ABC):
    @abstractmethod
    async def lookup_domain(self, domain: str) -> Optional[DomainIntelligenceSchema]:
        pass

    @abstractmethod
    def provider_name(self) -> str:
        pass

class ReputationProvider(ABC):
    @abstractmethod
    async def lookup_reputation(self, indicator: str, indicator_type: str) -> Optional[ReputationIntelligenceSchema]:
        pass

    @abstractmethod
    def provider_name(self) -> str:
        pass
