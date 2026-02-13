from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models.models import User, Preset, Pipeline
from app.services.preset_service import preset_service

router = APIRouter(prefix="/presets", tags=["presets"])

# Note: lifespan is handled in main.py, so we can't use startup_event here easily with async session.
# We will rely on a separate initialization script or lazy loading if needed.
# For now, we can omit automatic loading on startup here, or modify main.py.
# Prompt logic: "load_builtin_presets() - Load all JSON presets".
# We can expose an endpoint to trigger it, or just call it in main app startup.

@router.post("/initialize", tags=["admin"])
async def initialize_presets(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Optionally restrict to admin
):
    """Manually trigger loading of built-in presets."""
    loaded = await preset_service.load_builtin_presets(db)
    return {"message": f"Loaded {len(loaded)} presets"}

@router.get("", response_model=List[dict])
async def get_presets(
    category: Optional[str] = Query(None, description="Filter presets by category"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """List all available presets."""
    presets = await preset_service.get_all_presets(db, category)
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "tags": p.tags,
            "use_cases": p.use_cases,
            "thumbnail_url": p.thumbnail_url,
            "expected_metrics": p.expected_metrics
        }
        for p in presets
    ]

@router.get("/{preset_id}", response_model=dict)
async def get_preset_details(
    preset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get full details of a specific preset."""
    preset = await preset_service.get_preset_by_id(db, preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    return {
        "id": str(preset.id),
        "name": preset.name,
        "category": preset.category,
        "description": preset.description,
        "configuration": preset.configuration,
        "tags": preset.tags,
        "use_cases": preset.use_cases,
        "document_types": preset.document_types,
        "expected_metrics": preset.expected_metrics
    }

from sqlalchemy import select

@router.post("/{preset_id}/apply", response_model=dict)
async def apply_preset(
    preset_id: str,
    pipeline_name: Optional[str] = Query(None, description="Name for the new pipeline"),
    document_id: Optional[UUID] = Query(None, description="ID of the document to associate with the pipeline"),
    config_override: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a new pipeline from a preset, with optional config override and document association."""
    try:
        # Resolve 'default' keyword
        resolved_id = None
        if preset_id.lower() == "default":
            presets = await preset_service.get_all_presets(db)
            if presets:
                resolved_id = presets[0].id
            else:
                raise ValueError("No presets found to use as default")
        else:
            try:
                resolved_id = UUID(preset_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid UUID format for preset_id")

        if not current_user:
            # Check if token exists but user doesn't
            raise HTTPException(
                status_code=403, 
                detail="User account not found in database. Please Log Out and Log In again to sync your session."
            )
            
        user_id = current_user.id
            
        pipeline = await preset_service.apply_preset_to_pipeline(
            db, 
            resolved_id, 
            user_id,
            pipeline_name,
            custom_config=config_override,
            document_id=document_id
        )
        
        # Debug logging
        debug_msg = f"\n=== PIPELINE CREATED ===\nPipeline ID: {pipeline.id}\nPipeline Name: {pipeline.name}\nDocument ID passed: {document_id}\nSettings stored: {pipeline.settings}\n========================\n"
        print(debug_msg, flush=True)
        with open("debug_log.txt", "a") as f:
            f.write(debug_msg)
        
        return {
            "message": "Pipeline created successfully from preset",
            "pipeline_id": str(pipeline.id),
            "pipeline_name": pipeline.name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"\n!!! PRESET APPLY ERROR !!!\n{str(e)}\n{traceback.format_exc()}\n", flush=True)
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.exception("preset_apply_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
