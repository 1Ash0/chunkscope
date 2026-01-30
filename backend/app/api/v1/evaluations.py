"""
Evaluation Endpoints
CRUD operations for RAG evaluations and A/B testing
"""
from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy import func, select

from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.logging import get_logger
from app.dependencies import CurrentUser, DbSession
from app.models import Evaluation, EvaluationResult, Pipeline, TestDataset
from app.schemas import (
    EvaluationCreate,
    EvaluationListResponse,
    EvaluationResponse,
    EvaluationResultListResponse,
    EvaluationResultResponse,
    PaginationParams,
    SuccessResponse,
    paginate,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_evaluation(
    request: EvaluationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> EvaluationResponse:
    """
    Create and queue a new evaluation.
    
    Returns 202 Accepted as evaluation runs in background.
    """
    # Verify pipeline exists and user owns it
    pipeline = await db.execute(
        select(Pipeline).where(
            Pipeline.id == request.pipeline_id,
            Pipeline.user_id == current_user.id,
        )
    )
    if not pipeline.scalar_one_or_none():
        raise NotFoundError("Pipeline", str(request.pipeline_id))
    
    # Verify test dataset exists and user owns it
    dataset = await db.execute(
        select(TestDataset).where(
            TestDataset.id == request.test_dataset_id,
            TestDataset.user_id == current_user.id,
        )
    )
    if not dataset.scalar_one_or_none():
        raise NotFoundError("TestDataset", str(request.test_dataset_id))
    
    # Create evaluation record
    evaluation = Evaluation(
        user_id=current_user.id,
        name=request.name,
        pipeline_id=request.pipeline_id,
        test_dataset_id=request.test_dataset_id,
        comparison_pipeline_id=request.comparison_pipeline_id,
    )
    db.add(evaluation)
    await db.flush()
    await db.refresh(evaluation)
    
    # TODO: Queue background task with Celery
    # celery_app.send_task("run_evaluation", args=[str(evaluation.id)])
    
    logger.info(
        "evaluation_created",
        evaluation_id=str(evaluation.id),
        pipeline_id=str(request.pipeline_id),
    )
    
    return EvaluationResponse.model_validate(evaluation)


@router.get("", response_model=EvaluationListResponse)
async def list_evaluations(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    pipeline_id: UUID | None = Query(default=None, description="Filter by pipeline"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status"),
) -> EvaluationListResponse:
    """List user's evaluations with optional filters."""
    params = PaginationParams(page=page, per_page=per_page)
    
    base_query = select(Evaluation).where(Evaluation.user_id == current_user.id)
    
    if pipeline_id:
        base_query = base_query.where(Evaluation.pipeline_id == pipeline_id)
    if status_filter:
        base_query = base_query.where(Evaluation.status == status_filter)
    
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = (
        base_query
        .order_by(Evaluation.created_at.desc())
        .offset(params.offset)
        .limit(params.per_page)
    )
    result = await db.execute(query)
    evaluations = result.scalars().all()
    
    return paginate(
        items=[EvaluationResponse.model_validate(e) for e in evaluations],
        total=total,
        params=params,
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> EvaluationResponse:
    """Get evaluation with aggregate scores."""
    evaluation = await _get_user_evaluation(db, evaluation_id, current_user.id)
    return EvaluationResponse.model_validate(evaluation)


@router.get("/{evaluation_id}/results", response_model=EvaluationResultListResponse)
async def get_evaluation_results(
    evaluation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
) -> EvaluationResultListResponse:
    """Get individual query results for an evaluation."""
    # Verify ownership
    await _get_user_evaluation(db, evaluation_id, current_user.id)
    
    params = PaginationParams(page=page, per_page=per_page)
    
    count_query = select(func.count(EvaluationResult.id)).where(
        EvaluationResult.evaluation_id == evaluation_id
    )
    total = (await db.execute(count_query)).scalar() or 0
    
    query = (
        select(EvaluationResult)
        .where(EvaluationResult.evaluation_id == evaluation_id)
        .order_by(EvaluationResult.created_at)
        .offset(params.offset)
        .limit(params.per_page)
    )
    result = await db.execute(query)
    results = result.scalars().all()
    
    return paginate(
        items=[EvaluationResultResponse.model_validate(r) for r in results],
        total=total,
        params=params,
    )


@router.delete("/{evaluation_id}", response_model=SuccessResponse)
async def delete_evaluation(
    evaluation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> SuccessResponse:
    """Delete an evaluation and its results."""
    evaluation = await _get_user_evaluation(db, evaluation_id, current_user.id)
    await db.delete(evaluation)
    
    return SuccessResponse(message="Evaluation deleted successfully")


async def _get_user_evaluation(db: DbSession, evaluation_id: UUID, user_id: UUID) -> Evaluation:
    """Helper to get evaluation and verify ownership."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise NotFoundError("Evaluation", str(evaluation_id))
    
    if evaluation.user_id != user_id:
        raise PermissionDeniedError("You don't have access to this evaluation")
    
    return evaluation
