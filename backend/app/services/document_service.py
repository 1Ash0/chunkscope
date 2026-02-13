"""
Document Service
Business logic for document upload, validation, and processing
"""
import os
import uuid
from pathlib import Path
from typing import BinaryIO

import aiofiles
from fastapi import UploadFile

from app.config import settings
from app.core.errors import BadRequestError
from app.core.logging import get_logger
from app.core.database import async_session_maker
from app.models import Document, DocumentType, Chunk, ChunkingMethod
from app.services.pdf_processor import pdf_processor
from app.services.chunker import apply_chunking
from sqlalchemy import select, update, func
from fastapi.concurrency import run_in_threadpool

logger = get_logger(__name__)

# PDF magic bytes
PDF_MAGIC_BYTES = b"%PDF"

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {
    "application/pdf": DocumentType.PDF,
    "text/plain": DocumentType.TXT,
    "text/markdown": DocumentType.MD,
}

# File extension to DocumentType mapping
EXTENSION_TO_TYPE = {
    ".pdf": DocumentType.PDF,
    ".txt": DocumentType.TXT,
    ".md": DocumentType.MD,
    ".docx": DocumentType.DOCX,
    ".html": DocumentType.HTML,
    ".htm": DocumentType.HTML,
}


class DocumentService:
    """Service for document operations."""
    
    def __init__(self, upload_dir: str | None = None):
        self.upload_dir = Path(upload_dir or settings.upload_dir)
        self.max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    
    async def validate_upload(self, file: UploadFile) -> DocumentType:
        """
        Validate uploaded file.
        
        Returns:
            DocumentType if valid
            
        Raises:
            BadRequestError: If file is invalid
        """
        # Check filename
        if not file.filename:
            raise BadRequestError("Filename is required")
        
        # Check extension
        ext = Path(file.filename).suffix.lower()
        if ext not in EXTENSION_TO_TYPE:
            raise BadRequestError(
                f"Invalid file type '{ext}'. Allowed: {', '.join(EXTENSION_TO_TYPE.keys())}"
            )
        
        # Check content type (if provided)
        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            # Allow if extension is valid (content_type can be unreliable)
            logger.warning(
                "content_type_mismatch",
                filename=file.filename,
                content_type=file.content_type,
            )
        
        # For PDFs, validate magic bytes
        if ext == ".pdf":
            header = await file.read(4)
            await file.seek(0)  # Reset position
            
            if header != PDF_MAGIC_BYTES:
                raise BadRequestError("Invalid PDF file (corrupted or not a PDF)")
        
        # Check file size by reading chunks
        total_size = 0
        chunk_size = 64 * 1024  # 64KB chunks
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            
            if total_size > self.max_size_bytes:
                raise BadRequestError(
                    f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
                )
        
        # Reset file position for later reading
        await file.seek(0)
        
        return EXTENSION_TO_TYPE[ext]
    
    async def save_file(self, file: UploadFile, file_type: DocumentType) -> tuple[str, str, int]:
        """
        Save uploaded file to disk.
        
        Returns:
            Tuple of (stored_filename, file_path, file_size_bytes)
        """
        # Generate unique filename
        ext = Path(file.filename or "file").suffix.lower()
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.upload_dir / stored_filename
        
        # Stream file to disk
        total_bytes = 0
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(64 * 1024)  # 64KB chunks
                if not chunk:
                    break
                await f.write(chunk)
                total_bytes += len(chunk)
        
        logger.info(
            "file_saved",
            filename=stored_filename,
            original_filename=file.filename,
            size_bytes=total_bytes,
        )
        
        return stored_filename, str(file_path), total_bytes
    
        if path.exists():
            path.unlink()
            logger.info("file_deleted", path=file_path)
            return True
        return False

    async def process_document(self, document_id: uuid.UUID) -> bool:
        """
        Process a document to extract text and metadata.
        
        This method is designed to run in the background.
        It manages its own database session.
        """
        logger.info("processing_started", document_id=str(document_id))
        
        async with async_session_maker() as db:
            try:
                # Fetch document
                result = await db.execute(select(Document).where(Document.id == document_id))
                document = result.scalar_one_or_none()
                
                if not document:
                    logger.error("processing_failed", error="Document not found", document_id=str(document_id))
                    return False
                
                # Verify file exists
                file_path = Path(document.file_path)
                if not file_path.exists():
                    logger.error("processing_failed", error="File not found", path=str(file_path))
                    return False
                
                # Process based on type
                if document.file_type == DocumentType.PDF:
                    # Run extraction in thread pool to avoid blocking
                    extracted_doc = await run_in_threadpool(
                        pdf_processor.extract_document, 
                        file_path
                    )
                    
                    # Update document
                    document.extracted_text = extracted_doc.full_text
                    
                    # Merge metadata
                    current_metadata = document.doc_metadata or {}
                    new_metadata = extracted_doc.metadata.model_dump(mode='json', exclude_none=True)
                    current_metadata.update(new_metadata)
                    
                    # Add processing stats
                    current_metadata["page_count"] = extracted_doc.page_count
                    current_metadata["extraction_time_ms"] = extracted_doc.extraction_time_ms
                    current_metadata["total_blocks"] = extracted_doc.total_blocks
                    current_metadata["total_tables"] = extracted_doc.total_tables
                    
                    document.doc_metadata = current_metadata
                    document.is_processed = True
                    
                    # ---------------------------------------------------------
                    # Generate Default Chunks (Recursive, 512, 50)
                    # ---------------------------------------------------------
                    if document.extracted_text:
                        logger.info("generating_default_chunks", document_id=str(document_id))
                        chunks_data = apply_chunking(
                            text=document.extracted_text,
                            method="recursive",
                            chunk_size=512,
                            overlap=50
                        )
                        
                        db_chunks = []
                        for i, c_data in enumerate(chunks_data):
                            new_chunk = Chunk(
                                document_id=document_id,
                                text=c_data["text"],
                                chunk_index=i,
                                chunking_method=ChunkingMethod.RECURSIVE,
                                chunk_size=512,
                                chunk_overlap=50,
                                chunk_metadata={"start": c_data["start"], "end": c_data["end"]}
                            )
                            db_chunks.append(new_chunk)
                        
                        if db_chunks:
                            db.add_all(db_chunks)
                            logger.info("default_chunks_generated", document_id=str(document_id), count=len(db_chunks))

                    # Save changes
                    db.add(document)
                    await db.commit()
                    
                    logger.info(
                        "processing_completed", 
                        document_id=str(document_id),
                        pages=extracted_doc.page_count,
                        time_ms=extracted_doc.extraction_time_ms
                    )
                    return True
                
                else:
                    logger.warning("processing_skipped", reason="Unsupported type", type=document.file_type)
                    return False
                    
            except Exception as e:
                logger.error("processing_failed", document_id=str(document_id), error=str(e))
                # Optionally update document status to failed if we had a status field
                # For now just log it
                return False


# Singleton instance
document_service = DocumentService()
