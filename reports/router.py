from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db

from . import service
from .schemas import CompetencyScoreReportRow

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/cycles/{cycle_id}/competency-scores",
    response_model=list[CompetencyScoreReportRow],
)
async def get_cycle_competency_scores(
    cycle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.get_cycle_competency_scores(
        db=db,
        cycle_id=cycle_id,
    )
