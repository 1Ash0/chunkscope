from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import select, text
from app.models import Chunk
from app.services.retrievers.base import BaseRetriever
from app.dependencies import DbSession

class ParentDocumentRetriever(BaseRetriever):
    """
    Retrieves small chunks but returns larger parent context.
    Uses the parent_chunk_id to find larger context.
    """
    
    def __init__(self, db: DbSession):
        self.db = db

    async def retrieve(
        self, 
        query: str, 
        top_k: int = 5, 
        document_id: UUID = None,
        query_embedding: List[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Perform Parent Document retrieval."""
        if not query_embedding:
            return []
            
        # 1. Fetch children (small chunks)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # We look for chunks that HAVE a parent_chunk_id (children)
        # and are similar to the query.
        stmt = (
            select(
                Chunk,
                (1 - Chunk.embedding.cosine_distance(text(f"'{embedding_str}'::vector"))).label("score")
            )
            .where(Chunk.parent_chunk_id.isnot(None))
            .order_by(text("score DESC"))
            .limit(top_k * 2) # Fetch extra to account for duplicate parents
        )
        
        if document_id:
            stmt = stmt.where(Chunk.document_id == document_id)
            
        result = await self.db.execute(stmt)
        children = result.all()
        
        if not children:
            # Fallback to normal retrieval if no children found
            stmt_fallback = (
                select(
                    Chunk,
                    (1 - Chunk.embedding.cosine_distance(text(f"'{embedding_str}'::vector"))).label("score")
                )
                .order_by(text("score DESC"))
                .limit(top_k)
            )
            if document_id:
                stmt_fallback = stmt_fallback.where(Chunk.document_id == document_id)
            result = await self.db.execute(stmt_fallback)
            return [{"chunk": row.Chunk, "score": float(row.score)} for row in result.all()]

        # 2. Group by parent_chunk_id and keep highest score
        parent_scores = {}
        for row in children:
            pid = row.Chunk.parent_chunk_id
            if pid not in parent_scores or row.score > parent_scores[pid]["score"]:
                parent_scores[pid] = {"score": float(row.score), "child_id": row.Chunk.id}
                
        # 3. Fetch parent chunks
        parent_ids = list(parent_scores.keys())
        parent_stmt = select(Chunk).where(Chunk.id.in_(parent_ids))
        parent_result = await self.db.execute(parent_stmt)
        parents = parent_result.scalars().all()
        
        # 4. Map back and sort
        final_results = []
        for p in parents:
            final_results.append({
                "chunk": p,
                "score": parent_scores[p.id]["score"],
                "metadata": {"child_id": str(parent_scores[p.id]["child_id"])}
            })
            
        # Sort and return top_k
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results[:top_k]
