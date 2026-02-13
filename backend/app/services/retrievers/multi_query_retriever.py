import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.services.retrievers.base import BaseRetriever
from app.services.query_augmentor import query_augmentor
from app.services.rerankers.rrf_reranker import ReciprocalRankFusionReranker

class MultiQueryRetriever(BaseRetriever):
    """
    Retriever that generates multiple queries and combines results using RRF.
    """
    
    def __init__(self, base_retriever: BaseRetriever, num_variants: int = 3):
        self.base_retriever = base_retriever
        self.num_variants = num_variants
        self.rrf = ReciprocalRankFusionReranker(k=60)

    async def retrieve(
        self, 
        query: str, 
        top_k: int = 10, 
        document_id: Optional[UUID] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        # 1. Generate query variants
        queries = await query_augmentor.augment_multi_query(query, self.num_variants)
        
        # 2. Retrieve for each variant in parallel
        tasks = [
            self.base_retriever.retrieve(q, top_k=top_k, document_id=document_id, **kwargs)
            for q in queries
        ]
        results_lists = await asyncio.gather(*tasks)
        
        # 3. Combine results using RRF
        combined_results = await self.rrf.fuse(results_lists, top_k=top_k)
        
        # Add metadata about which queries were used
        for res in combined_results:
            res["metadata"] = res.get("metadata", {})
            res["metadata"]["augmented_queries"] = queries
            
        return combined_results
