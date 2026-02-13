import logging
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class QueryAugmentor:
    """
    Service for augmenting user queries using LLMs.
    Supports Multi-Query generation, HyDE, and Query Expansion.
    """
    
    _cache = {}

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            logger.warning("OpenAI API key not found. Query augmentation will run in simulation mode.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def _get_completion(self, system_prompt: str, user_prompt: str, cache_key: str) -> str:
        """Helper to get completion with simple in-memory caching."""
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.client:
            return "SIMULATED RESPONSE: No API Key provided."

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=300
            )
            content = response.choices[0].message.content
            self._cache[cache_key] = content
            return content
        except Exception as e:
            logger.error(f"LLM augmentation failed: {e}")
            return user_prompt # Fallback to original

    async def augment_multi_query(self, query: str, num_variants: int = 3) -> List[str]:
        """Generate multiple variants of the query."""
        system_prompt = (
            f"You are a search query optimizer. Generate {num_variants} different variations "
            "of the user's search query to improve retrieval coverage. "
            "Return ONLY a JSON list of strings."
        )
        user_prompt = f"Original Query: {query}"
        cache_key = f"multi_{query}_{num_variants}"
        
        response_text = await self._get_completion(system_prompt, user_prompt, cache_key)
        
        try:
            # Try to parse as JSON list
            variants = json.loads(response_text)
            if isinstance(variants, list):
                # Ensure original is included if not present
                if query not in variants:
                    variants = [query] + variants[:num_variants-1]
                return [str(v) for v in variants]
        except:
            # Fallback parsing
            lines = [l.strip().strip('"') for l in response_text.split('\n') if l.strip()]
            variants = [l for l in lines if l and not l.startswith('[') and not l.startswith(']')]
            if not variants:
                return [query]
            return variants[:num_variants]

    async def augment_hyde(self, query: str) -> str:
        """Generate a hypothetical document (HyDE)."""
        system_prompt = (
            "You are a helpful assistant. Provide a brief, hypothetical answer "
            "to the user's search query. This answer will be used to improve "
            "semantic search by matching against potential documents."
        )
        user_prompt = f"Query: {query}"
        cache_key = f"hyde_{query}"
        
        return await self._get_completion(system_prompt, user_prompt, cache_key)

    async def augment_expansion(self, query: str) -> str:
        """Expand the query with synonyms and related terms."""
        system_prompt = (
            "You are a search optimizer. Expand the user's query with relevant "
            "keywords, synonyms, and technical terms to improve recall. "
            "Return the original query followed by the expanded terms."
        )
        user_prompt = f"Query: {query}"
        cache_key = f"expand_{query}"
        
        return await self._get_completion(system_prompt, user_prompt, cache_key)

query_augmentor = QueryAugmentor()
