from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from models.cycles import Cycle, CycleStatus
from models.appraisal import Appraisal


async def create(db: AsyncSession, name: str, start_date: datetime, end_date: datetime) -> Cycle:
    cycle = Cycle(name=name, start_date=start_date, end_date=end_date, status=CycleStatus.INITIATED)
    db.add(cycle)
    await db.commit()
    await db.refresh(cycle)
    return cycle


async def get_all_cycles(db: AsyncSession):
    stmt = select(Cycle).where(Cycle.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.all()


async def get_filter_cycles(status_filter: CycleStatus, db: AsyncSession):
    stmt = select(Cycle).where(Cycle.status == status_filter, Cycle.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.all()


async def get_cycle_by_id(cycle_id: int, db: AsyncSession) -> Cycle | None:
    stmt = select(Cycle).where(Cycle.id == cycle_id, Cycle.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.first()


async def get_active_appraisals_by_cycle(cycle_id: int, db: AsyncSession):
    stmt = select(Appraisal).where(Appraisal.cycle_id == cycle_id, Appraisal.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.all()


async def get_assigned_employee_ids(cycle_id: int, db: AsyncSession) -> list[int]:
    stmt = select(Appraisal.employee_id).where(Appraisal.cycle_id == cycle_id, Appraisal.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return list(result.all())


async def add_appraisal_assignments(db: AsyncSession, appraisals: list[Appraisal]) -> list[Appraisal]:
    db.add_all(appraisals)
    await db.commit()
    for appraisal in appraisals:
        await db.refresh(appraisal)
    return appraisals


async def get_assignment_by_emp(cycle_id: int, employee_id: int, db: AsyncSession) -> Appraisal | None:
    stmt = select(Appraisal).where(
        Appraisal.cycle_id == cycle_id, Appraisal.employee_id == employee_id, Appraisal.deleted_at.is_(None)
    )
    result = await db.scalars(stmt)
    return result.first()


async def save_changes(db: AsyncSession):
    await db.commit()
