from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import valid service
from app.services.pipeline_executor import PipelineExecutor

router = APIRouter()

class PipelineRequest(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = {}

@router.post("/execute")
async def execute_pipeline(request: PipelineRequest):
    """
    Execute a RAG pipeline based on the provided graph.
    """
    try:
        executor = PipelineExecutor(
            nodes=request.nodes,
            edges=request.edges
        )
        
        # In a real app, we might run this in background
        # using BackgroundTasks if long-running.
        # For this phase, we await result directly.
        results = await executor.execute()
        
        return {
            "status": "success",
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
