from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from auth.schemas import TokenPayload
from database import get_db
from models.user import UserRole
from auth.dependencies import get_current_user, require_role
from summaries import service
from summaries.schemas import SummaryCreate, SummaryUpdate, SummaryResponse

router = APIRouter(prefix="/appraisal-summaries", tags=["Appraisal Summaries"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SummaryResponse,
)
async def generate_appraisal_summary(
    body: SummaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.generate_summary(body, db)


@router.get("/{summary_id}", response_model=SummaryResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def get_summary_by_id(summary_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_summary_by_id(summary_id, db)


@router.get(
    "/appraisal/{appraisal_id}", response_model=SummaryResponse, dependencies=[Depends(require_role(UserRole.HR))]
)
async def get_summary_by_appraisal_id(appraisal_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_summary_by_appraisal(appraisal_id, db)


@router.put("/{summary_id}", response_model=SummaryResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def update_appraisal_summary(summary_id: int, body: SummaryUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_summary(summary_id, body, db)


@router.delete(
    "/{summary_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(UserRole.HR))]
)
async def delete_appraisal_summary(summary_id: int, db: AsyncSession = Depends(get_db)):
    await service.soft_delete_summary(summary_id, db)
    return None
