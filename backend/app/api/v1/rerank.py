from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.reranker import reranker_service

router = APIRouter()

class RerankRequest(BaseModel):
    query: str
    documents: List[Dict[str, Any]]
    method: Optional[str] = "cohere"
    model: Optional[str] = None
    top_k: Optional[int] = 5
    parameters: Optional[Dict[str, Any]] = {}

@router.post("/")
async def rerank_documents(request: RerankRequest):
    """
    Rerank a list of documents based on a query.
    """
    try:
        # Resolve model name if not provided
        model = request.model
        if not model:
            if request.method == "cohere":
                model = "rerank-english-v3.0"
            elif request.method == "cross-encoder":
                model = "cross-encoder/ms-marco-MiniLM-L-12-v2"
        
        reranker = reranker_service.get_reranker(
            provider=request.method,
            model=model,
            **request.parameters
        )
        
        results = await reranker.rerank(
            query=request.query,
            documents=request.documents,
            top_k=request.top_k
        )
        
        return {
            "status": "success",
            "results": results,
            "count": len(results),
            "method": request.method,
            "model": model
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
