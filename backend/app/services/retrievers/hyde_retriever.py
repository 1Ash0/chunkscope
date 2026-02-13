from typing import List, Dict, Any, Optional
from uuid import UUID
from app.services.retrievers.base import BaseRetriever
from app.services.query_augmentor import query_augmentor

class HyDERetriever(BaseRetriever):
    """
    Hypothetical Document Embedding (HyDE) retriever.
    Generates a hypothetical answer and uses it for semantic search.
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
        # 1. Generate hypothetical document
        hyde_doc = await query_augmentor.augment_hyde(query)
        
        # 2. Retrieve using the hypothetical document instead of the query
        results = await self.base_retriever.retrieve(
            hyde_doc, 
            top_k=top_k, 
            document_id=document_id, 
            **kwargs
        )
        
        # Add metadata
        for res in results:
            res["metadata"] = res.get("metadata", {})
            res["metadata"]["hyde_document"] = hyde_doc
            res["metadata"]["original_query"] = query
            
        return results
