"""
Preview Endpoints
Operations for real-time preview of chunking and processing.
"""
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.services.chunker import apply_chunking
from app.schemas import ChunkingConfig, ChunkMetrics

router = APIRouter(prefix="/preview", tags=["Preview"])

class ChunkPreviewRequest(BaseModel):
    """Request for real-time chunking preview."""
    text: str = Field(..., description="Text to chunk")
    config: ChunkingConfig = Field(default_factory=ChunkingConfig)

class ChunkPreviewItem(BaseModel):
    """A single chunk in the preview."""
    id: str
    text: str
    start: int
    end: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChunkPreviewResponse(BaseModel):
    """Response for chunking preview."""
    chunks: List[ChunkPreviewItem]
    metrics: ChunkMetrics

@router.post("/chunking", response_model=ChunkPreviewResponse)
async def preview_chunking(request: ChunkPreviewRequest) -> ChunkPreviewResponse:
    """
    Apply chunking to the provided text and return chunks with offsets.
    Used for real-time visualization in the UI.
    """
    start_time = time.time()
    
    # Apply chunking
    chunks_data = apply_chunking(
        text=request.text,
        method=request.config.method,
        chunk_size=request.config.chunk_size,
        overlap=request.config.overlap,
    )
    
    # Map to response format
    final_chunks = []
    for i, c in enumerate(chunks_data):
        final_chunks.append(
            ChunkPreviewItem(
                id=f"preview_{i}",
                text=c["text"],
                start=c["start"],
                end=c["end"],
                metadata={"index": i}
            )
        )
        
    # Calculate metrics
    chunk_sizes = [len(c["text"]) for c in chunks_data]
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    metrics = ChunkMetrics(
        total_chunks=len(final_chunks),
        avg_chunk_size=sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
        min_chunk_size=min(chunk_sizes) if chunk_sizes else 0,
        max_chunk_size=max(chunk_sizes) if chunk_sizes else 0,
        processing_time_ms=processing_time_ms,
    )
    
    return ChunkPreviewResponse(
        chunks=final_chunks,
        metrics=metrics
    )
