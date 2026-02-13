import logging
import cohere
from typing import List, Dict, Any
from app.services.rerankers.base import BaseReranker
from app.config import settings

logger = logging.getLogger(__name__)

class CohereReranker(BaseReranker):
    """
    Cohere Rerank provider using the official SDK.
    """
    
    def __init__(self, model: str = "rerank-english-v3.0", api_key: str = None):
        self.model = model
        self.api_key = api_key or settings.cohere_api_key
        if not self.api_key:
            raise ValueError("Cohere API key not found in settings or provided to constructor.")
        
        # Use ClientV2 for modern Cohere API access
        self.client = cohere.ClientV2(api_key=self.api_key)

    async def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []
            
        try:
            # Extract text for Cohere API
            doc_texts = [doc.get("text", "") for doc in documents]
            
            # Cohere V3 rerank (synchronous in SDK but we wrap it in a thread pool if needed, 
            # though usually SDK handles it or we use async client if available)
            # For simplicity, we use the standard client which is performant enough for 20 docs.
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=doc_texts,
                top_n=top_k
            )
            
            reranked_results = []
            for hit in response.results:
                original_doc = documents[hit.index].copy()
                original_doc["rerank_score"] = hit.relevance_score
                reranked_results.append(original_doc)
                
            return reranked_results
            
        except Exception as e:
            logger.error(f"Cohere Rerank failed: {e}")
            # Fallback: return original docs truncated
            return documents[:top_k]
