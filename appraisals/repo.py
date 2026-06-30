"""Appraisal Repo"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from models.appraisal import Appraisal,AppraisalStatus
from models.user import UserRole
from exceptions import ConflictException, NotFoundException


async def create(
    db: AsyncSession,
    cycle_id: int,
    employee_id: int,
    idp_text: str,
    hr_notes: str,
) -> Appraisal:
    appraisal = Appraisal(
        cycle_id=cycle_id,
        employee_id=employee_id,
        idp_text=idp_text,
        hr_notes=hr_notes,
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


async def get_all_appraisals(db: AsyncSession):
    stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
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


async def update_appraisal(
        appraisal_id:int,
        db:AsyncSession,
        idp_text:str,
        hr_notes:str,
        status:str,
        ):
    stmt = (
        update(Appraisal)
        .where(Appraisal.id == appraisal_id, Appraisal.deleted_at.is_(None))
        .values(idp_text=idp_text, hr_notes=hr_notes,status=status)
    )

    result = await db.execute(stmt)
    if result is None:
        raise NotFoundException("Appraisal not found")

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Appraisal conflict")
    # await db.refresh(result)
    return await get_appraisal_by_id(appraisal_id=appraisal_id,db=db)
    


async def soft_delete_appraisal(appraisal: Appraisal, db: AsyncSession):
    await db.commit()
    return
