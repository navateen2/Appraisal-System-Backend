"""Appraisal Repo"""

import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from models.appraisal import Appraisal,AppraisalStatus
from exceptions import ConflictException


async def create(
    db: AsyncSession,
    cycle_id: int,
    employee_id: int,
) -> Appraisal:
    appraisal = Appraisal(
        cycle_id=cycle_id,
        employee_id=employee_id,
        status=AppraisalStatus.Initiated
        )
    
    db.add(appraisal)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        print(e)
        raise ConflictException(f"Appraisal conflict error")
    await db.refresh(appraisal)
    return appraisal


async def get_all_appraisals(db: AsyncSession, status: str|None):
    stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
    if status:
        stmt = stmt.where(Appraisal.status == status)
    result = await db.scalars(stmt)
    return result


# async def get_filter_users(filter: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     return result


async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession):
    stmt = select(Appraisal).where(Appraisal.id == appraisal_id, Appraisal.deleted_at.is_(None))
    result = await db.scalars(stmt)
    appraisal = result.first()
    return appraisal


# async def get_appraisal_by_name(appraisal_name: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.name == appraisal_name, Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     user = result.first()
#     return user


# async def get_by_email(db: AsyncSession, email: str) -> Appraisal | None:
#     stmt = select(Appraisal).where(Appraisal.email == email, Appraisal.deleted_at.is_(None))
#     user = await db.scalars(stmt)
#     return user.first()
 


async def soft_delete_appraisal(appraisal: Appraisal, db: AsyncSession):
    await db.commit()
    return

async def update_appraisal_idp(db: AsyncSession, appraisal: Appraisal, idp_text: str) -> Appraisal:
    appraisal.idp_text = idp_text
    appraisal.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(appraisal)
    return appraisal


async def update_appraisal_hr_notes(db: AsyncSession, appraisal: Appraisal, hr_notes: str) -> Appraisal:
    appraisal.hr_notes = hr_notes
    appraisal.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(appraisal)
    return appraisal

async def get_employee_appraisal_history(db: AsyncSession, employee_id: int) -> List[Appraisal]:
    stmt = (
        select(Appraisal)
        .options(joinedload(Appraisal.cycle))
        .filter(Appraisal.employee_id == employee_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_appraisal_status(db: AsyncSession, appraisal: Appraisal, status: AppraisalStatus) -> Appraisal:
    appraisal.status = status
    await db.commit()
    await db.refresh(appraisal)
    return appraisal

async def get_detailed_appraisal_by_id(db: AsyncSession, appraisal_id: int) -> Appraisal | None:
    stmt = (
        select(Appraisal)
        .options(
            selectinload(Appraisal.self_appraisal),
            selectinload(Appraisal.lead_assignments)
        )
        .filter(Appraisal.id == appraisal_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()