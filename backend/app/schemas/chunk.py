"""
Chunk Visualization Schemas
Request/response models for chunk visualization and processing
"""
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


# ============================================
# Chunking Configuration
# ============================================

class ChunkingConfig(BaseModel):
    """Configuration for chunking algorithm."""
    method: str = Field(
        default="fixed",
        description="Chunking method: fixed, semantic, recursive, sentence, paragraph"
    )
    chunk_size: int = Field(default=512, ge=10, le=10000, description="Target chunk size in characters")
    min_chunk_size: int = Field(default=100, ge=10, description="Minimum chunk size to avoid small fragments")
    overlap: int = Field(default=50, ge=0, description="Overlap between chunks")
    threshold: float = Field(default=0.5, ge=0, le=1, description="Similarity threshold for semantic chunking (0-1)")
    threshold_percentile: int = Field(default=90, ge=0, le=100, description="Percentile for semantic splitting (0-100)")
    window_size: int = Field(default=1, ge=0, le=10, description="Number of sentences to include in context window (0=sentence only)")


class BoundingBox(BaseModel):
    """Bounding box coordinates for chunk visualization."""
    page: int = Field(ge=1, description="Page number (1-indexed)")
    x: float = Field(ge=0, description="X coordinate from left")
    y: float = Field(ge=0, description="Y coordinate from top")
    width: float = Field(ge=0, description="Width in points")
    height: float = Field(ge=0, description="Height in points")


# ============================================
# Request Schemas
# ============================================

class ChunkVisualizeRequest(BaseModel):
    """Request to visualize document chunks."""
    document_id: UUID
    chunking_config: ChunkingConfig = Field(default_factory=ChunkingConfig)


# ============================================
# Response Schemas
# ============================================

class ChunkVisualization(BaseModel):
    """A single chunk with visualization data."""
    id: str
    text: str
    bbox: BoundingBox | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkMetrics(BaseModel):
    """Metrics about the chunking process."""
    total_chunks: int
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int
    total_tokens: int = 0
    processing_time_ms: int


class ChunkReturn(BaseModel):
    """Returned chunk object with text and positions."""
    text: str
    start_char: int
    end_char: int
    token_count: Optional[int] = None


class ChunkVisualizeResponse(BaseSchema):
    """Response for chunk visualization."""
    document_id: UUID
    chunks: list[ChunkVisualization]
    metrics: ChunkMetrics
