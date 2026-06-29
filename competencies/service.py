from sqlalchemy.ext.asyncio import AsyncSession
from models.competencies import Competencies
from exceptions import NotFoundException
from competencies import repo

async def create(db: AsyncSession, name: str) -> Competencies: 
    competency = await repo.create(db, name=name)
    return competency

async def get_all_competencies(db: AsyncSession):
    return await repo.get_all_competencies(db)

async def get_competency_by_id(competency_id: int, db: AsyncSession):
    competency = await repo.get_competency_by_id(competency_id, db)
    if competency is None:
        raise NotFoundException(f"Competency with id: {competency_id} not found")
    return competency

async def update_competency(competency_id: int, name: str, db: AsyncSession):
    rows_affected = await repo.update_competency_direct(competency_id, name, db) 
    if rows_affected == 0:
        raise NotFoundException(f"Competency with id {competency_id} not found")
    return {"id": competency_id, "name": name}

async def delete_competency(competency_id: int, db: AsyncSession):
    rows_affected = await repo.delete_competency_direct(competency_id, db)
    if rows_affected == 0:
        raise NotFoundException(f"Competency with id: {competency_id} not found")
    return