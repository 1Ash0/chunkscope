
"""
Document Analysis API Endpoints
"""
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import hash_password
from app.core.errors import AppException
from app.services.document_analyzer import document_analyzer
from app.services.document_service import document_service
from app.models import User, Document
from app import dependencies as deps

logger = get_logger(__name__)

router = APIRouter(prefix="/analyze", tags=["analysis"])


class AnalysisResponse(BaseModel):
    """Response schema for document analysis."""
    document_id: Optional[UUID] = None
    document_type: str
    structure: Dict
    density: Dict
    recommended_config: Dict
    confidence_score: float
    reasoning: str


@router.post("", response_model=AnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Analyze a uploaded document.
    
    If user is authenticated, saves the document.
    If anonymous, uses/creates a default 'demo' user to save the document so visualizer works.
    """
    
    # Handling Anonymous Users: Ensure we always have a user to save the document
    if not current_user:
        try:
            # Try to find the specific Demo User
            result = await db.execute(select(User).where(User.email == "demo@chunkscope.com"))
            current_user = result.scalars().first()
            
            if not current_user:
                logger.info("No users found. Creating 'Demo User' for anonymous analysis.")
                current_user = User(
                    email="demo@chunkscope.com",
                    password_hash=hash_password("demo123"), # Correct field name
                    name="Demo User" # Correct field name
                )
                db.add(current_user)
                await db.commit()
                await db.refresh(current_user)
            else:
                logger.info(f"Using default user '{current_user.email}' for anonymous analysis.")
        except Exception as e:
            # Import traceback to print it
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to setup anonymous user: {e}")
            # Continue without user if DB fails, but saving will likely fail
            pass

    document_id = None
    temp_path = None
    
    try:
        # Validate and save file using document service
        # Note: document_service usually requires a user_id, but we'll manually create the Document object here
        # to ensure we use our retrieved/created current_user
        
        file_type = await document_service.validate_upload(file)
        stored_filename, file_path, file_size = await document_service.save_file(file, file_type)
        temp_path = file_path # Keep track for cleanup if needed
        
        if current_user:
            # Create Document record linked to the user
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
            await db.commit()
            await db.refresh(document)
            
            document_id = document.id
            
            # Start extraction in background
            background_tasks.add_task(document_service.process_document, document_id)
        
        # Analyze the document
        logger.info(f"Analyzing file: {file.filename}, document_id={document_id}")
        
        # Run analysis
        result = await document_analyzer.analyze(file_path)
        
        # Debug logging
        debug_msg = f"\n=== ANALYSIS COMPLETE ===\nFile: {file.filename}\nUser: {current_user.email if current_user else 'None'}\nDocument ID: {document_id}\n=========================\n"
        print(debug_msg, flush=True)
        try:
            with open("debug_log.txt", "a") as f:
                f.write(debug_msg)
        except Exception:
            pass
        
        return AnalysisResponse(
            document_id=document_id,
            **result
        )

    except Exception as e:
        if isinstance(e, AppException):
            raise e
            
        import traceback
        error_msg = f"\n!!! ANALYSIS FAILED !!!\nError: {str(e)}\nTraceback:\n{traceback.format_exc()}\n=======================\n"
        print(error_msg, flush=True)
        try:
            with open("debug_log.txt", "a") as f:
                f.write(error_msg)
        except Exception:
            pass
            
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
