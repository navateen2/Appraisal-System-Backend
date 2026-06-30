from sqlalchemy.ext.asyncio import AsyncSession

from appraisals.service import get_appraisal_by_id
from exceptions import ForbiddenException, NotFoundException
from models.user import UserRole

from . import repo
from .schemas import (
    LeadRecommendationResponse,
    RecommendedLead,
)


async def create(
    db: AsyncSession,
    appraisal_id: int,
    recommended_lead_ids: list[int],
    employee_id: int,
) -> LeadRecommendationResponse:

    appraisal = await get_appraisal_by_id(
        db=db,
        appraisal_id=appraisal_id,
    )

    if appraisal.employee_id != employee_id:
        raise ForbiddenException(
            "This appraisal does not belong to the current user."
        )

    await repo.create(
        db=db,
        appraisal_id=appraisal_id,
        recommended_lead_ids=recommended_lead_ids,
    )

    return LeadRecommendationResponse(
        status="Lead recommendations updated successfully.",
        recommended_lead_ids=recommended_lead_ids,
    )
    
    
async def get_by_appraisal_id(
    db: AsyncSession,
    appraisal_id: int,
    employee_id: int,
    user_role:UserRole,
) -> list[RecommendedLead]:

    appraisal = await get_appraisal_by_id(
        db=db,
        appraisal_id=appraisal_id,
    )

    if (appraisal.employee_id != employee_id and not user_role is UserRole.HR):
        raise ForbiddenException(
            "You are not allowed to view these recommendations."
        )

    recommendations = await repo.get_ELRs_by_appraisal_id(
        db=db,
        appraisal_id=appraisal_id,
    )

    return [
        RecommendedLead(
            recommended_lead_id=row["recommended_lead_id"],
            name=row["name"],
            email=row["email"],
        )
        for row in recommendations
    ]