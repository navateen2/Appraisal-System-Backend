from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.dependencies import require_role, get_current_user
from auth.schemas import TokenPayload
from models.user import UserRole
from lead_assignments import service
from lead_assignments.schemas import AssignLeadsRequest, LeadAssignmentResponse, AssignedLeadProfileResponse
from typing import List

router = APIRouter()

@router.post(
    "/{appraisal_id}/leads",
    status_code=status.HTTP_201_CREATED,
    response_model=List[LeadAssignmentResponse],
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def assign_leads(
    appraisal_id: int,
    body: AssignLeadsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    return await service.assign_leads_to_appraisal(appraisal_id, body.lead_ids, current_user.id, db) # current user id 

@router.get(
    "/{appraisal_id}/leads",
    response_model=List[AssignedLeadProfileResponse],
    dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))]
)
async def get_assigned_leads(
    appraisal_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_assigned_leads(appraisal_id, db)

@router.delete(
    "/{appraisal_id}/leads/{lead_id}",
    response_model=str,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def remove_assigned_lead(
    appraisal_id: int,
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    await service.remove_assigned_lead(appraisal_id, lead_id, db)
    return "Lead assignment and pending feedbacks successfully cleaned up"