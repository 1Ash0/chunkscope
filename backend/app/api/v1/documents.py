"""
Document Endpoints
CRUD operations for uploaded documents
"""
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Query, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy import func, select

from app.core.errors import BadRequestError, NotFoundError, PermissionDeniedError
from app.core.logging import get_logger
from app.dependencies import CurrentUser, CurrentUserOptional, DbSession
from app.models import Document, User
from app.schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentDetailResponse,
    PaginationParams,
    SuccessResponse,
    paginate,
)
from app.services.document_service import document_service

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="PDF, TXT, or MD file to upload"),
) -> DocumentResponse:
    """
    Upload a document for processing.
    
    Accepts PDF, TXT, and MD files up to 100MB.
    """
    # Validate file
    try:
        file_type = await document_service.validate_upload(file)
    except BadRequestError:
        raise
    except Exception as e:
        logger.error("upload_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File validation failed: {str(e)}"
        )
    
    # Save file to disk
    try:
        stored_filename, file_path, file_size = await document_service.save_file(file, file_type)
    except Exception as e:
        logger.error("upload_save_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Create database record
    document = Document(
        user_id=current_user.id,
        filename=stored_filename,
        original_filename=file.filename or "unknown",
        file_path=file_path,
        file_type=file_type.value,
        file_size_bytes=file_size,
        doc_metadata={},
        is_processed=False,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    
    logger.info(
        "document_uploaded",
        document_id=str(document.id),
        filename=file.filename,
        size_bytes=file_size,
    )
    
    # Trigger processing in background
    background_tasks.add_task(document_service.process_document, document.id)
    
    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    file_type: str | None = Query(default=None, description="Filter by file type"),
) -> DocumentListResponse:
    """List all documents for the current user."""
    params = PaginationParams(page=page, per_page=per_page)
    
    # Base query
    base_query = select(Document).where(Document.user_id == current_user.id)
    
    if file_type:
        base_query = base_query.where(Document.file_type == file_type)
    
    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Fetch items
    query = (
        base_query
        .order_by(Document.created_at.desc())
        .offset(params.offset)
        .limit(params.per_page)
    )
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return paginate(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        params=params,
    )


from fastapi.responses import FileResponse

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: UUID,
    db: DbSession,
    current_user: CurrentUserOptional,
):
    """Get the actual file content of a document."""
    try:
        # Fetch document with user info
        from sqlalchemy.orm import joinedload
        
        query = select(Document).options(joinedload(Document.user)).where(Document.id == document_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise NotFoundError("Document", str(document_id))
        
        # Ensure user is loaded
        if not document.user:
             # Fallback fetch
             res = await db.execute(select(User).where(User.id == document.user_id))
             document.user = res.scalar_one_or_none()

        # Check access: Allow if owner OR if it's a demo document
        doc_email = document.user.email if document.user else ""
        is_demo_doc = doc_email == "demo@chunkscope.com"
        is_owner = current_user and document.user_id == current_user.id
        
        if not (is_demo_doc or is_owner):
            raise PermissionDeniedError("You don't have access to this document")

        if not Path(document.file_path).exists():
            raise NotFoundError("File", document.file_path)
            
        return FileResponse(
            path=document.file_path,
            filename=document.original_filename,
            media_type="application/pdf" if document.file_type == "pdf" else "application/octet-stream"
        )
    except Exception as e:
        import traceback
        with open("backend_error.log", "a") as f:
            f.write(f"Error in get_document_content: {str(e)}\n")
            f.write(traceback.format_exc())
            f.write("\n" + "="*30 + "\n")
        raise e


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> DocumentDetailResponse:
    """Get a specific document by ID."""
    document = await _get_user_document(db, document_id, current_user.id)
    return DocumentDetailResponse.model_validate(document)


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> SuccessResponse:
    """Delete a document and its chunks."""
    document = await _get_user_document(db, document_id, current_user.id)
    await db.delete(document)
    
    return SuccessResponse(message="Document deleted successfully")


async def _get_user_document(db: DbSession, document_id: UUID, user_id: UUID) -> Document:
    """Helper to get a document and verify ownership."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundError("Document", str(document_id))
    
    if document.user_id != user_id:
        raise PermissionDeniedError("You don't have access to this document")
    
    return document
