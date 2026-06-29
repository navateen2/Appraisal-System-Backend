"""Self Appraisal Repo"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.self_appraisal import SelfAppraisal


async def create(db: AsyncSession, self_appraisal: SelfAppraisal) -> SelfAppraisal:
    db.add(self_appraisal)
    await db.commit()
    await db.refresh(self_appraisal)
    return self_appraisal


async def get_all(db: AsyncSession):
    stmt = select(SelfAppraisal)
    result = await db.scalars(stmt)
    return result


async def get_by_id(db: AsyncSession, self_appraisal_id: int):
    stmt = select(SelfAppraisal).where(SelfAppraisal.id == self_appraisal_id)
    result = await db.scalars(stmt)
    return result.first()


async def update(db: AsyncSession, self_appraisal: SelfAppraisal):
    await db.commit()
    await db.refresh(self_appraisal)
    return self_appraisal


async def delete(db: AsyncSession, self_appraisal: SelfAppraisal):
    await db.delete(self_appraisal)
    await db.commit()
    return

async def get_by_appraisal_id(db: AsyncSession, appraisal_id: int):
    stmt = select(SelfAppraisal).where(
        SelfAppraisal.appraisal_id == appraisal_id
    )
    result = await db.scalars(stmt)
    return result.first()
