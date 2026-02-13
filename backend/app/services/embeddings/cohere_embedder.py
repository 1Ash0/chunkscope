import logging
from typing import List
import cohere
from app.services.embeddings.base import BaseEmbedder
from app.config import settings

logger = logging.getLogger(__name__)

class CohereEmbedder(BaseEmbedder):
    """
    Cohere embedding provider.
    """
    
    def __init__(self, model_name: str = "embed-english-v3.0", api_key: str = None):
        self._model_name = model_name
        self.api_key = api_key or settings.cohere_api_key
        if not self.api_key:
            raise ValueError("Cohere API key matches neither node config nor .env settings.")
        
        self.client = cohere.ClientV2(api_key=self.api_key)
        
        # Metadata based on common Cohere models
        self._meta = {
            "embed-english-v3.0": {"dim": 1024, "cost": 0.1},
            "embed-multilingual-v3.0": {"dim": 1024, "cost": 0.1},
            "embed-english-light-v3.0": {"dim": 384, "cost": 0.1},
            "embed-multilingual-light-v3.0": {"dim": 384, "cost": 0.1},
            "embed-english-v2.0": {"dim": 4096, "cost": 0.1},
        }

    @property
    def provider_name(self) -> str:
        return "cohere"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._meta.get(self._model_name, {}).get("dim", 1024)

    @property
    def cost_per_million_tokens(self) -> float:
        return self._meta.get(self._model_name, {}).get("cost", 0.1)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            # Cohere V3 models require input_type
            input_type = "search_document"
            
            response = self.client.embed(
                texts=texts,
                model=self._model_name,
                input_type=input_type,
                embedding_types=["float"]
            )
            # ClientV2 response structure
            return response.embeddings.float
        except Exception as e:
            logger.error(f"Cohere embedding failed: {e}")
            raise
