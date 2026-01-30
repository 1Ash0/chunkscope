"""
Chunk Endpoints
Operations for text chunks and vector search
"""
import time
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select, text

from app.core.errors import BadRequestError, NotFoundError
from app.core.logging import get_logger
from app.dependencies import CurrentUser, DbSession
from app.models import Chunk, Document
from app.schemas import (
    ChunkingConfig,
    ChunkListResponse,
    ChunkMetrics,
    ChunkResponse,
    ChunkVisualization,
    ChunkVisualizeRequest,
    ChunkVisualizeResponse,
    ChunkWithSimilarity,
    PaginationParams,
    paginate,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/chunks", tags=["Chunks"])


@router.post("/visualize", response_model=ChunkVisualizeResponse)
async def visualize_chunks(
    request: ChunkVisualizeRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ChunkVisualizeResponse:
    """
    Process a document with the specified chunking configuration.
    
    Returns chunks with bounding box coordinates for visualization.
    """
    start_time = time.time()
    
    # Verify document exists and user owns it
    result = await db.execute(
        select(Document).where(
            Document.id == request.document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundError("Document", str(request.document_id))
    
    # Check if document has extracted text
    if not document.extracted_text:
        raise BadRequestError("Document has not been processed. Text extraction required.")
    
    config = request.chunking_config
    
    # Validate configuration
    if config.overlap >= config.chunk_size:
        raise BadRequestError("Overlap must be less than chunk_size")
    
    # Apply chunking strategy
    chunks_data = _apply_chunking(
        text=document.extracted_text,
        method=config.method,
        chunk_size=config.chunk_size,
        overlap=config.overlap,
    )
    
    # Build response
    chunk_sizes = [len(c["text"]) for c in chunks_data]
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    metrics = ChunkMetrics(
        total_chunks=len(chunks_data),
        avg_chunk_size=sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
        min_chunk_size=min(chunk_sizes) if chunk_sizes else 0,
        max_chunk_size=max(chunk_sizes) if chunk_sizes else 0,
        processing_time_ms=processing_time_ms,
    )
    
    chunks = [
        ChunkVisualization(
            id=f"chunk_{i}",
            text=c["text"],
            bbox=c.get("bbox"),
            metadata={"char_start": c.get("start", 0), "char_end": c.get("end", 0)},
        )
        for i, c in enumerate(chunks_data)
    ]
    
    logger.info(
        "chunks_visualized",
        document_id=str(document.id),
        method=config.method,
        chunk_count=len(chunks),
        processing_time_ms=processing_time_ms,
    )
    
    return ChunkVisualizeResponse(
        document_id=document.id,
        chunks=chunks,
        metrics=metrics,
    )


def _apply_chunking(
    text: str,
    method: str,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Apply chunking strategy to text."""
    if method == "fixed":
        return _fixed_size_chunking(text, chunk_size, overlap)
    elif method == "sentence":
        return _sentence_chunking(text, chunk_size, overlap)
    elif method == "paragraph":
        return _paragraph_chunking(text, chunk_size)
    elif method == "recursive":
        return _recursive_chunking(text, chunk_size, overlap)
    else:
        # Default to fixed
        return _fixed_size_chunking(text, chunk_size, overlap)


def _fixed_size_chunking(text: str, chunk_size: int, overlap: int) -> list[dict]:
    """Simple fixed-size chunking with overlap."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "text": text[start:end],
            "start": start,
            "end": end,
        })
        start = end - overlap if end < len(text) else len(text)
    
    return chunks


def _sentence_chunking(text: str, chunk_size: int, overlap: int) -> list[dict]:
    """Chunk by sentences, respecting chunk_size limit."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    current_start = 0
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
                "end": current_start + len(current_chunk),
            })
            # Apply overlap by keeping last portion
            overlap_text = current_chunk[-overlap:] if overlap else ""
            current_start = current_start + len(current_chunk) - len(overlap_text)
            current_chunk = overlap_text
        
        current_chunk += sentence + " "
    
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start,
            "end": current_start + len(current_chunk),
        })
    
    return chunks


def _paragraph_chunking(text: str, chunk_size: int) -> list[dict]:
    """Chunk by paragraphs."""
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    current_start = 0
    char_pos = 0
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
                "end": current_start + len(current_chunk),
            })
            current_start = char_pos
            current_chunk = ""
        
        current_chunk += para + "\n\n"
        char_pos += len(para) + 2
    
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start,
            "end": current_start + len(current_chunk),
        })
    
    return chunks


def _recursive_chunking(text: str, chunk_size: int, overlap: int) -> list[dict]:
    """Recursive character text splitter (LangChain style)."""
    separators = ["\n\n", "\n", ". ", " ", ""]
    
    def split_text(text: str, separators: list[str]) -> list[str]:
        if not separators:
            return [text]
        
        separator = separators[0]
        splits = text.split(separator) if separator else list(text)
        
        chunks = []
        current = ""
        
        for split in splits:
            piece = split + separator if separator else split
            if len(current) + len(piece) > chunk_size:
                if current:
                    chunks.append(current)
                if len(piece) > chunk_size:
                    chunks.extend(split_text(piece, separators[1:]))
                    current = ""
                else:
                    current = piece
            else:
                current += piece
        
        if current:
            chunks.append(current)
        
        return chunks
    
    raw_chunks = split_text(text, separators)
    
    # Add position info
    chunks = []
    pos = 0
    for chunk in raw_chunks:
        chunks.append({
            "text": chunk,
            "start": pos,
            "end": pos + len(chunk),
        })
        pos += len(chunk)
    
    return chunks


@router.get("/document/{document_id}", response_model=ChunkListResponse)
async def list_document_chunks(
    document_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
) -> ChunkListResponse:
    """List all chunks for a document."""
    params = PaginationParams(page=page, per_page=per_page)
    
    # Verify document ownership
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if not doc_result.scalar_one_or_none():
        raise NotFoundError("Document", str(document_id))
    
    # Count total
    count_query = select(func.count(Chunk.id)).where(Chunk.document_id == document_id)
    total = (await db.execute(count_query)).scalar() or 0
    
    # Fetch chunks
    query = (
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
        .offset(params.offset)
        .limit(params.per_page)
    )
    result = await db.execute(query)
    chunks = result.scalars().all()
    
    return paginate(
        items=[ChunkResponse.model_validate(c) for c in chunks],
        total=total,
        params=params,
    )


@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ChunkResponse:
    """Get a specific chunk by ID."""
    result = await db.execute(
        select(Chunk)
        .join(Document)
        .where(
            Chunk.id == chunk_id,
            Document.user_id == current_user.id,
        )
    )
    chunk = result.scalar_one_or_none()
    
    if not chunk:
        raise NotFoundError("Chunk", str(chunk_id))
    
    return ChunkResponse.model_validate(chunk)


@router.get("/search/similar", response_model=list[ChunkWithSimilarity])
async def search_similar_chunks(
    db: DbSession,
    current_user: CurrentUser,
    query_embedding: str = Query(
        description="Comma-separated embedding vector (1536 dimensions)"
    ),
    document_id: UUID | None = Query(default=None, description="Limit to specific document"),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ChunkWithSimilarity]:
    """
    Search for similar chunks using vector similarity.
    Requires a pre-computed query embedding.
    """
    # Parse embedding from query param
    try:
        embedding_values = [float(x.strip()) for x in query_embedding.split(",")]
        if len(embedding_values) != 1536:
            raise ValueError(f"Expected 1536 dimensions, got {len(embedding_values)}")
    except ValueError as e:
        raise ValueError(f"Invalid embedding format: {e}")
    
    # Build query with cosine similarity
    embedding_str = f"[{','.join(map(str, embedding_values))}]"
    
    base_query = (
        select(
            Chunk,
            (1 - Chunk.embedding.cosine_distance(text(f"'{embedding_str}'::vector"))).label("similarity")
        )
        .join(Document)
        .where(Document.user_id == current_user.id)
    )
    
    if document_id:
        base_query = base_query.where(Chunk.document_id == document_id)
    
    query = (
        base_query
        .order_by(text("similarity DESC"))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        ChunkWithSimilarity(
            **ChunkResponse.model_validate(row.Chunk).model_dump(),
            similarity=row.similarity,
        )
        for row in rows
    ]
