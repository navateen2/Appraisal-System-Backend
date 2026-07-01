from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db

from . import service
from .schemas import (
    FeedbackQuestionnaireRequest,
    FeedbackQuestionnaireResponse,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Feedback Assistant"],
)


@router.post(
    "/feedback-questionnaire",
    response_model=FeedbackQuestionnaireResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_feedback_questionnaire(
    payload: FeedbackQuestionnaireRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    questionnaire = await service.generate_feedback_questionnaire(
        competencies=payload.competencies,
    )

    return questionnaire
