from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, select, update
from models.competencies import Competencies
from exceptions import ConflictException

async def create(db: AsyncSession, name: str) -> Competencies:
    competency = Competencies(name=name)
    db.add(competency)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Competency name '{name}' already exists")
    await db.refresh(competency)
    return competency

async def get_all_competencies(db: AsyncSession):
    stmt = select(Competencies)
    result = await db.scalars(stmt)
    return result.all()

async def get_competency_by_id(competency_id: int, db: AsyncSession):
    stmt = select(Competencies).where(Competencies.id == competency_id)
    result = await db.scalars(stmt)
    competency = result.first()
    return competency

async def update_competency_direct(competency_id: int, name: str, db: AsyncSession) -> int:
    stmt = (
        update(Competencies)
        .where(Competencies.id == competency_id)
        .values(name=name)
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount 
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Competency name '{name}' already exists")

async def delete_competency_direct(competency_id: int, db: AsyncSession) -> int:
    stmt = (
        delete(Competencies)
        .where(Competencies.id == competency_id)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount