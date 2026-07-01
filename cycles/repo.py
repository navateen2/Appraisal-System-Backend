from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from models.cycles import Cycles, CycleStatus
from models.appraisal import Appraisal
from models.user import User


async def create(db: AsyncSession, name: str, start_date: datetime, end_date: datetime, current_user_id: int) -> Cycles:
    cycle = Cycles(
        name=name, start_date=start_date, end_date=end_date, status=CycleStatus.Initiated, created_by_id=current_user_id
    )
    db.add(cycle)
    await db.commit()
    await db.refresh(cycle)
    return cycle


async def get_all_cycles(db: AsyncSession):
    stmt = select(Cycles).where(Cycles.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.all()


async def get_filter_cycles(status_filter: CycleStatus, db: AsyncSession):
    stmt = select(Cycles).where(Cycles.status == status_filter, Cycles.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.all()


async def get_cycle_by_id(cycle_id: int, db: AsyncSession) -> Cycles | None:
    stmt = select(Cycles).where(Cycles.id == cycle_id, Cycles.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.first()


async def get_active_appraisals_by_cycle(cycle_id: int, db: AsyncSession):
    stmt = (
        select(
            Appraisal.id,
            Appraisal.employee_id,
            Appraisal.status,
            User.name.label("employee_name"),
        )
        .join(
            User,
            User.id == Appraisal.employee_id,
        )
        .where(
            Appraisal.cycle_id == cycle_id,
            Appraisal.deleted_at.is_(None),
        )
    )

    result = await db.execute(stmt)
    return result.mappings().all()


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


async def save_changes(db: AsyncSession, instance=None):
    await db.commit()

    if instance:
        await db.refresh(instance)
