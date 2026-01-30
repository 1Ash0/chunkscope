"""
Configuration Schemas
Request/response models for configuration and recommendations
"""
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


# ============================================
# Document Analysis
# ============================================

class DocumentAnalyzeRequest(BaseModel):
    """Request to analyze a document."""
    document_id: UUID


class DocumentCharacteristics(BaseModel):
    """Detected document characteristics."""
    avg_sentence_length: float = 0
    vocabulary_richness: float = 0
    has_tables: bool = False
    has_code_blocks: bool = False
    has_lists: bool = False
    has_headings: bool = False
    page_count: int = 0
    word_count: int = 0


class PipelineRecommendation(BaseModel):
    """Recommended pipeline configuration."""
    chunker: str = Field(description="Recommended chunking method")
    chunk_size: int = Field(description="Recommended chunk size")
    overlap: int = Field(description="Recommended overlap")
    embedding_model: str = Field(description="Recommended embedding model")
    retrieval_method: str = Field(description="Recommended retrieval method")
    confidence: float = Field(ge=0, le=1, description="Confidence in recommendation")
    explanation: str = Field(description="Why this configuration is recommended")


class DocumentAnalyzeResponse(BaseSchema):
    """Response for document analysis."""
    document_id: UUID
    document_type: str = Field(description="Detected type: legal, technical, narrative, etc.")
    structure: str = Field(description="Detected structure: hierarchical, flat, etc.")
    characteristics: DocumentCharacteristics
    recommendations: PipelineRecommendation


# ============================================
# Pipeline Validation
# ============================================

class PipelineValidateRequest(BaseModel):
    """Request to validate pipeline configuration."""
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class ValidationIssue(BaseModel):
    """A validation warning or error."""
    type: str = Field(description="warning or error")
    node_id: Optional[str] = None
    message: str


class PipelineValidateResponse(BaseSchema):
    """Response for pipeline validation."""
    valid: bool
    warnings: list[ValidationIssue] = Field(default_factory=list)
    errors: list[ValidationIssue] = Field(default_factory=list)
    estimated_cost_per_1k_docs: float = 0.0
