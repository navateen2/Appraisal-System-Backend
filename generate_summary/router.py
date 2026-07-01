from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db

from . import service
from generate_summary.schemas import (
    AppraisalSummaryRequest,
    AppraisalSummaryResponse,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Summary"],
)


@router.post(
    "/appraisal-summary",
    response_model=AppraisalSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_appraisal_summary(
    payload: AppraisalSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """
    Generate an AI summary for an appraisal.
    """

    summary = await service.generate_appraisal_summary(
        db=db,
        appraisal_id=payload.appraisal_id,
    )

    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appraisal not found.",
        )

    return AppraisalSummaryResponse(
        appraisal_id=payload.appraisal_id,
        summary=summary,
    )
