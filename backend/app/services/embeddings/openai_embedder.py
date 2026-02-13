import logging
from typing import List
from app.services.embeddings.base import BaseEmbedder
from app.config import settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI embedding provider using AsyncOpenAI.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None):
        self._model_name = model_name
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key matches neither node config nor .env settings.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Metadata based on common OpenAI models
        self._meta = {
            "text-embedding-3-small": {"dim": 1536, "cost": 0.02},
            "text-embedding-3-large": {"dim": 3072, "cost": 0.13},
            "text-embedding-ada-002": {"dim": 1536, "cost": 0.10},
        }

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._meta.get(self._model_name, {}).get("dim", 1536)

    @property
    def cost_per_million_tokens(self) -> float:
        return self._meta.get(self._model_name, {}).get("cost", 0.02)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self._model_name
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
