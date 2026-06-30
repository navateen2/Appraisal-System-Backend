from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import TokenPayload
from database import get_db
from fastapi import Depends, status, APIRouter
from lead_feedbacks import service
from models.user import UserRole
from lead_feedbacks.schemas import CreateFeedbackFormPayload, UpdateFeedbackFormPayload, FeedbackFormResponse
from auth.dependencies import require_role, get_current_user

router = APIRouter(prefix="/feedback", tags=["Lead Feedbacks"])

@router.post(
    "/mapping/{mapping_id}/form",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedbackFormResponse,
    dependencies=[Depends(require_role(UserRole.Employee))]
)
async def save_lead_feedback_form(
    mapping_id: int, 
    body: CreateFeedbackFormPayload, 
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    result = await service.save_feedback_form(mapping_id, body.items, current_user.id, db)
    return result

@router.put(
    "/mapping/{mapping_id}/form",
    response_model=FeedbackFormResponse,
    dependencies=[Depends(require_role(UserRole.Employee))]
)
async def update_lead_feedback_form(
    mapping_id: int, 
    body: UpdateFeedbackFormPayload, 
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    result = await service.update_feedback_form(mapping_id, body.items, current_user.id, db)
    return result

@router.get(
    "/mapping/{mapping_id}/form",
    response_model=FeedbackFormResponse,
    dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))]
)
async def get_lead_feedback_form(
    mapping_id: int, 
    db: AsyncSession = Depends(get_db),
):
    result = await service.get_feedback_form(mapping_id, db)
    return result