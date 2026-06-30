"""ELR Repo"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, insert, select, update
from models.associations import employee_lead_recommendations as ELR
from exceptions import ConflictException, NotFoundException
from models.user import User


async def create(
    db: AsyncSession,
    appraisal_id: int,
    recommended_lead_ids: list[int],
):
    await delete_ELRs_by_appraisal_id(db=db, appraisal_id=appraisal_id)

    values = [
        {
            "appraisal_id": appraisal_id,
            "recommended_lead_id": lead_id,
        }
        for lead_id in recommended_lead_ids
    ]

    try:
        await db.execute(insert(ELR), values)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            "Lead recommendation conflict."
        )

    return recommended_lead_ids


async def get_all_ELRs(db: AsyncSession):
    stmt = select(ELR)
    result = await db.execute(stmt)
    return result.mappings().all()


# async def get_filter_users(filter: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     return result

async def get_ELRs_by_appraisal_id(
    appraisal_id: int,
    db: AsyncSession,
):
    stmt = (
        select(
            ELR.c.recommended_lead_id,
            User.name,
            User.email,
        )
        .join(
            User,
            User.id == ELR.c.recommended_lead_id,
        )
        .where(
            ELR.c.appraisal_id == appraisal_id,
        )
    )

    result = await db.execute(stmt)

    return result.mappings().all()



async def delete_ELRs_by_appraisal_id(appraisal_id: int, db: AsyncSession):
    stmt =(
		delete(ELR)
		.where(ELR.c.appraisal_id == appraisal_id)
	)
    result = await db.execute(stmt)
    return result.rowcount

# async def get_elr_by_name(elr_name: str, db: AsyncSession):
#     stmt = select(Appraisal).where(Appraisal.name == elr_name, Appraisal.deleted_at.is_(None))
#     result = await db.scalars(stmt)
#     user = result.first()
#     return user


# async def get_by_email(db: AsyncSession, email: str) -> Appraisal | None:
#     stmt = select(Appraisal).where(Appraisal.email == email, Appraisal.deleted_at.is_(None))
#     user = await db.scalars(stmt)
#     return user.first()


# async def update_elr(
#         elr_id:int,
# 		recommended_lead_id: int,
# 		appraisal_id: int,
#         db:AsyncSession,
#         ):
#     stmt = (
#         update(ELR)
#         .where(ELR.id == elr_id, ELR.deleted_at.is_(None))
#         .values(recommended_lead_id=recommended_lead_id,appraisal_id=appraisal_id)
#     )

#     result = await db.execute(stmt)
#     if result is None:
#         raise NotFoundException

#     try:
#         await db.commit()
#     except IntegrityError:
#         await db.rollback()
#         raise ConflictException(f"Appraisal lead recommendation conflict")
#     # await db.refresh(result)
#     return await get_ELRs_by_appraisal_id(elr_id=elr_id,db=db)
    


# async def soft_delete_elr(elr: ELR, db: AsyncSession):
#     await db.commit()
#     return
