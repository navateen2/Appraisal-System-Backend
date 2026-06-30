from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import TokenPayload
from database.connection import get_db
from self_appraisals.schemas import SelfAppraisalCreate, SelfAppraisalResponse, SelfAppraisalUpdate
from auth.dependencies import get_current_user
from . import service

router = APIRouter(
    prefix="/self-appraisals",
    tags=["Self Appraisal"],
)


@router.post(
    "/",
    response_model=SelfAppraisalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_self_appraisal(
    payload: SelfAppraisalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.create_self_appraisal(db, payload)


@router.get(
    "/",
    response_model=list[SelfAppraisalResponse],
)
async def get_all_self_appraisals(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all_self_appraisals(db)


@router.get(
    "/{self_appraisal_id}",
    response_model=SelfAppraisalResponse,
)
async def get_self_appraisals(
    self_appraisal_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_self_appraisal_by_id(db, self_appraisal_id)


@router.put(
    "/{self_appraisal_id}",
    response_model=SelfAppraisalResponse,
)
async def update_self_appraisals(
    self_appraisal_id: int,
    payload: SelfAppraisalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.update_self_appraisal(db, self_appraisal_id, payload)


@router.delete(
    "/{self_appraisal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_self_apraisals(
    self_appraisal_id: int, db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)
):
    await service.delete_self_appraisal(db, self_appraisal_id)
    return None
