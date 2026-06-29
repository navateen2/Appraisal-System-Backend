from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from models.cycles import Cycle, CycleStatus
from models.appraisal import Appraisal
from exceptions import NotFoundException, BadRequestException
from cycles import repo
from cycles.schemas import CycleCreate, CycleUpdate, CycleStatusUpdate


async def create_cycle(body: CycleCreate, db: AsyncSession) -> Cycle:
    return await repo.create(db, name=body.name, start_date=body.start_date, end_date=body.end_date)


async def get_all_cycles(db: AsyncSession, status_filter: CycleStatus | None = None):
    if status_filter:
        return await repo.get_filter_cycles(status_filter, db)
    return await repo.get_all_cycles(db)


async def get_cycle_by_id(cycle_id: int, db: AsyncSession) -> Cycle:
    cycle = await repo.get_cycle_by_id(cycle_id, db)
    if cycle is None:
        raise NotFoundException(f"Cycle with id {cycle_id} not found")
    return cycle


async def update_cycle(cycle_id: int, body: CycleUpdate, db: AsyncSession) -> Cycle:
    cycle = await repo.get_cycle_by_id(cycle_id, db)
    if cycle is None:
        raise NotFoundException(f"Cycle with id {cycle_id} not found")

    if body.name is not None:
        cycle.name = body.name
    if body.start_date is not None:
        cycle.start_date = body.start_date
    if body.end_date is not None:
        cycle.end_date = body.end_date

    await repo.save_changes(db)
    return cycle


async def update_cycle_status(cycle_id: int, body: CycleStatusUpdate, db: AsyncSession) -> Cycle:
    cycle = await repo.get_cycle_by_id(cycle_id, db)
    if cycle is None:
        raise NotFoundException(f"Cycle with id {cycle_id} not found")

    if body.status == CycleStatus.COMPLETED:
        appraisals = await repo.get_active_appraisals_by_cycle(cycle_id, db)
        for app in appraisals:
            if app.status not in ["Meeting Done", "Done"]:
                raise BadRequestException(
                    "Cannot close cycle. All appraisals must be in 'Meeting Done' or 'Done' state."
                )

    cycle.status = body.status
    await repo.save_changes(db)
    return cycle


async def soft_delete_cycle(cycle_id: int, db: AsyncSession):
    cycle = await repo.get_cycle_by_id(cycle_id, db)
    if cycle is None:
        raise NotFoundException(f"Cycle with id {cycle_id} not found")
    cycle.deleted_at = datetime.utcnow()
    await repo.save_changes(db)


async def assign_employees_to_cycle(cycle_id: int, employee_ids: list[int], db: AsyncSession):
    cycle = await repo.get_cycle_by_id(cycle_id, db)
    if cycle is None:
        raise NotFoundException(f"Cycle with id {cycle_id} not found")

    existing_assigned = await repo.get_assigned_employee_ids(cycle_id, db)
    existing_set = set(existing_assigned)

    to_create = []
    skipped_ids = []

    for emp_id in employee_ids:
        if emp_id in existing_set:
            skipped_ids.append(emp_id)
        else:
            to_create.append(Appraisal(cycle_id=cycle_id, employee_id=emp_id, status="Initiated"))

    success_items = []
    if to_create:
        success_items = await repo.add_appraisal_assignments(db, to_create)

    return {"successfully_assigned": success_items, "already_assigned_employee_ids": skipped_ids}


async def remove_employee_assignment(cycle_id: int, employee_id: int, db: AsyncSession):
    appraisal = await repo.get_assignment_by_emp(cycle_id, employee_id, db)
    if appraisal is None:
        raise NotFoundException(f"Assignment for employee {employee_id} in cycle {cycle_id} not found")
    appraisal.deleted_at = datetime.utcnow()
    await repo.save_changes(db)
