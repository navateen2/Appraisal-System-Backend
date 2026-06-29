"""Appraisal Repo"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from models.appraisal_lead_reccomendation import ALR
from exceptions import ConflictException, NotFoundException


async def create(
    db: AsyncSession,
    reccomended_lead_id: int,
	appraisal_id: int,
) -> ALR:
    alr = ALR(
        reccomended_lead_id=reccomended_lead_id,
		appraisal_id=appraisal_id,
        )
    
    db.add(alr)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        print(e)
        raise ConflictException(f"Appraisal lead reccomendation conflict error")
    await db.refresh(alr)
    return alr


async def get_all_alrs(db: AsyncSession):
    stmt = select(ALR).where(ALR.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result


# async def get_filter_users(filter: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     return result


async def get_ALR_by_id(alr_id: int, db: AsyncSession):
    stmt = select(ALR).where(ALR.id == alr_id, ALR.deleted_at.is_(None))
    result = await db.scalars(stmt)
    alr = result.first()
    return alr


# async def get_alr_by_name(alr_name: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.name == alr_name, Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     user = result.first()
#     return user


# async def get_by_email(db: AsyncSession, email: str) -> Appraisal | None:
#     stmt = select(Appraisal).where(Appraisal.email == email, Appraisal.deleted_at.is_(None))
#     user = await db.scalars(stmt)
#     return user.first()


async def update_alr(
        alr_id:int,
		reccomended_lead_id: int,
		appraisal_id: int,
        db:AsyncSession,
        ):
    stmt = (
        update(ALR)
        .where(ALR.id == alr_id, ALR.deleted_at.is_(None))
        .values(reccomended_lead_id=reccomended_lead_id,appraisal_id=appraisal_id)
    )

    result = await db.execute(stmt)
    if result is None:
        raise NotFoundException

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Appraisal lead reccomendation conflict")
    # await db.refresh(result)
    return await get_ALR_by_id(alr_id=alr_id,db=db)
    


async def soft_delete_alr(alr: ALR, db: AsyncSession):
    await db.commit()
    return
