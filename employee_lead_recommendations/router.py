from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.connection import get_db
from models.user import User

from . import service
from .schemas import (
    LeadRecommendationRequest,
    LeadRecommendationResponse,
    RecommendedLead,
)

router = APIRouter(
    prefix="/appraisals",
    tags=["Lead Recommendations"],
)


@router.post(
    "/{appraisal_id}/lead-recommendations",
    response_model=LeadRecommendationResponse,
    status_code=status.HTTP_200_OK,
    
)
async def create_or_update_lead_recommendations(
    appraisal_id: int,
    request: LeadRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create or replace the list of recommended leads for an appraisal.
    """
    return await service.create(
        db=db,
        appraisal_id=appraisal_id,
        recommended_lead_ids=request.recommended_lead_ids,
        employee_id=current_user.id,
    )


@router.get(
    "/{appraisal_id}/lead-recommendations",
    response_model=list[RecommendedLead],
)
async def get_lead_recommendations(
    appraisal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all recommended leads for an appraisal.
    """
    return await service.get_by_appraisal_id(
        db=db,
        appraisal_id=appraisal_id,
        employee_id=current_user.id,
        user_role=current_user.role
    )