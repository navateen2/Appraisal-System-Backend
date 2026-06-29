"""Appraisal Service"""

from sqlalchemy.ext.asyncio import AsyncSession
from models.appraisal import Appraisal,AppraisalStatus
from .schemas import AppraisalResponse,AppraisalCreate,AppraisalResponseId
from models.user import UserRole
from datetime import datetime

from exceptions import NotFoundException, BadRequestException
from auth.utils import hash_password
from . import repo


async def create(
    db: AsyncSession,
    cycle_id: int,
    employee_id: int,
    idp_text: str,
    hr_notes: str,
) -> AppraisalResponse:
    user = await repo.create(db, cycle_id, employee_id,idp_text,hr_notes)
    return user


async def get_all_appraisals(db: AsyncSession):
    return await repo.get_all_appraisals(db)


# async def get_filter_appraisals(filter: str, db: AsyncSession):
#     if filter != "All":
#         return await repo.get_filter_users(filter, db)
#     return await repo.get_all_users(db)


# async def get_user_by_name(user_name: str, db: AsyncSession):
#     user = await repo.get_user_by_name(user_name, db)
#     if user is None:
#         raise NotFoundException("Users not found")
#     return user


async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if appraisal is None:
        raise NotFoundException(f"Appraisal with id: {appraisal_id} not found")
    return appraisal


async def update_appraisal(
        appraisal_id: int,
        db: AsyncSession,
        idp_text: str,
        hr_notes: str,
        status: str
        ):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if appraisal is None:
        raise NotFoundException(f"Appraisal with id {appraisal_id} not found")
    if not isinstance(idp_text, str) or not idp_text.strip():
        print(idp_text)
        raise BadRequestException("idp_text must be a non-empty string")
    if not isinstance(hr_notes, str):
        raise BadRequestException("hr_notes must be a string")
    try:
        status_enum = AppraisalStatus(status)
    except ValueError:
        raise BadRequestException("Invalid appraisal status")
    
    appraisal.idp_text = idp_text.strip()
    appraisal.hr_notes = hr_notes.strip()
    result = await repo.update_appraisal(
        appraisal_id=appraisal_id,
        db=db,
        idp_text=idp_text,
        hr_notes=hr_notes,
        status=status,
        )
    return result


async def soft_delete_appraisal(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if appraisal is None:
        raise NotFoundException(f"Appraisal with id:{appraisal_id} not found")
    appraisal.deleted_at = datetime.now()
    await repo.soft_delete_appraisal(appraisal, db)
    return
