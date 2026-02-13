from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseReranker(ABC):
    """
    Base class for all reranker implementations.
    """
    
    @abstractmethod
    async def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on the query.
        
        Args:
            query: The search query.
            documents: List of document dictionaries. Each should have a 'text' field.
            top_k: Number of final documents to return.
            
        Returns:
            List of reranked document dictionaries with 'rerank_score' added.
        """
        pass
