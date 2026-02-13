from typing import List, Dict, Any, Optional
from uuid import UUID
from app.services.retrievers.base import BaseRetriever
from app.services.query_augmentor import query_augmentor

class QueryExpansionRetriever(BaseRetriever):
    """
    Retriever that expands the query with synonyms/terms before searching.
    """
    
    def __init__(self, base_retriever: BaseRetriever):
        self.base_retriever = base_retriever

    async def retrieve(
        self, 
        query: str, 
        top_k: int = 10, 
        document_id: Optional[UUID] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        # 1. Expand query
        expanded_query = await query_augmentor.augment_expansion(query)
        
        # 2. Retrieve using expanded query
        results = await self.base_retriever.retrieve(
            expanded_query, 
            top_k=top_k, 
            document_id=document_id, 
            **kwargs
        )
        
        # Add metadata
        for res in results:
            res["metadata"] = res.get("metadata", {})
            res["metadata"]["expanded_query"] = expanded_query
            
        return results
