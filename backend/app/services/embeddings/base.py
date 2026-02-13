from abc import ABC, abstractmethod
from typing import List

class BaseEmbedder(ABC):
    """
    Abstract base class for all embedding providers.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'openai', 'local')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the specific model being used."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Embedding vector dimensions."""
        pass

    @property
    @abstractmethod
    def cost_per_million_tokens(self) -> float:
        """Cost in USD per 1M tokens."""
        pass

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        pass
