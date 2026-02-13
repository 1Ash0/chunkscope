from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import UUID

class BaseRetriever(ABC):
    """Base class for all retrievers."""
    
    @abstractmethod
    async def retrieve(
        self, 
        query: str, 
        top_k: int = 10, 
        document_id: UUID = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Returns a list of dicts containing chunk data and score.
        """
        pass
