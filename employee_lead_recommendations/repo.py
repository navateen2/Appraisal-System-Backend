"""Appraisal Repo"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from models.employee_lead_recommendation import ELR
from exceptions import ConflictException, NotFoundException


async def create(
    db: AsyncSession,
    reccomended_lead_ids: list[int],
	appraisal_id: int,
) -> ELR:
	for i in reccomended_lead_ids:
		elr = ELR(
			reccomended_lead_id=i,
			appraisal_id=appraisal_id,
			)
		
	db.add(elr)
	try:
		await db.commit()
	except IntegrityError as e:
		await db.rollback()
		print(e)
		raise ConflictException(f"Appraisal lead reccomendation conflict error")
	await db.refresh(elr)
	return elr


async def get_all_elrs(db: AsyncSession):
    stmt = select(ELR).where(ELR.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result


# async def get_filter_users(filter: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     return result


async def get_ELR_by_id(elr_id: int, db: AsyncSession):
    stmt = select(ELR).where(ELR.id == elr_id, ELR.deleted_at.is_(None))
    result = await db.scalars(stmt)
    elr = result.first()
    return elr


# async def get_elr_by_name(elr_name: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.name == elr_name, Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     user = result.first()
#     return user


# async def get_by_email(db: AsyncSession, email: str) -> Appraisal | None:
#     stmt = select(Appraisal).where(Appraisal.email == email, Appraisal.deleted_at.is_(None))
#     user = await db.scalars(stmt)
#     return user.first()


async def update_elr(
        elr_id:int,
		reccomended_lead_id: int,
		appraisal_id: int,
        db:AsyncSession,
        ):
    stmt = (
        update(ELR)
        .where(ELR.id == elr_id, ELR.deleted_at.is_(None))
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
    return await get_ELR_by_id(elr_id=elr_id,db=db)
    


async def soft_delete_elr(elr: ELR, db: AsyncSession):
    await db.commit()
    return
