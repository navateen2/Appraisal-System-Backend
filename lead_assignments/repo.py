import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import NotFoundException
from models.appraisal import Appraisal, AppraisalStatus
from models.appraisal_lead_assignment import AppraisalLeadAssignment, AssignmentStatus
from models.cycles import Cycles
from models.lead_feedback import LeadFeedback
from models.associations import employee_lead_recommendations
from typing import List

from models.user import User


async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession) -> Appraisal | None:
    stmt = select(Appraisal).where(Appraisal.id == appraisal_id, Appraisal.deleted_at.is_(None))
    res = await db.scalars(stmt)
    return res.first()


async def get_assignment_by_id(mapping_id: int, db: AsyncSession) -> AppraisalLeadAssignment | None:
    stmt = (
        select(AppraisalLeadAssignment)
        .options(selectinload(AppraisalLeadAssignment.appraisal))
        .where(AppraisalLeadAssignment.id == mapping_id, AppraisalLeadAssignment.deleted_at.is_(None))
    )
    res = await db.scalars(stmt)
    return res.first()


async def get_existing_assigned_lead_ids(appraisal_id: int, db: AsyncSession) -> List[int]:
    stmt = select(AppraisalLeadAssignment.lead_id).where(
        AppraisalLeadAssignment.appraisal_id == appraisal_id, AppraisalLeadAssignment.deleted_at.is_(None)
    )
    res = await db.scalars(stmt)
    return list(res.all())


async def get_recommended_lead_ids(appraisal_id: int, db: AsyncSession) -> List[int]:
    stmt = select(employee_lead_recommendations.c.recommended_lead_id).where(
        employee_lead_recommendations.c.appraisal_id == appraisal_id
    )
    res = await db.scalars(stmt)
    return list(res.all())


async def bulk_create_assignments(
    appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession
) -> List[AppraisalLeadAssignment]:
    for l_id in lead_ids:
        assignment = AppraisalLeadAssignment(
            appraisal_id=appraisal_id, lead_id=l_id, assigned_by=hr_id, status=AssignmentStatus.Pending
        )
        db.add(assignment)
    await db.commit()

    stmt = (
        select(AppraisalLeadAssignment)
        .where(AppraisalLeadAssignment.appraisal_id == appraisal_id)
        .where(AppraisalLeadAssignment.lead_id.in_(lead_ids))
    )
    res = await db.scalars(stmt)
    return list(res.all())


async def get_assigned_leads_with_profiles(appraisal_id: int, db: AsyncSession) -> List[AppraisalLeadAssignment]:
    stmt = (
        select(AppraisalLeadAssignment)
        .options(selectinload(AppraisalLeadAssignment.lead))
        .where(AppraisalLeadAssignment.appraisal_id == appraisal_id, AppraisalLeadAssignment.deleted_at.is_(None))
    )
    res = await db.scalars(stmt)
    return list(res.all())


async def delete_assignment_cascade(assignment: AppraisalLeadAssignment, db: AsyncSession):
    current_time = datetime.utcnow()

    feedback_cleanup_stmt = (
        update(LeadFeedback)
        .where(LeadFeedback.mapping_id == assignment.id, LeadFeedback.deleted_at.is_(None))
        .values(deleted_at=current_time)
    )
    await db.execute(feedback_cleanup_stmt)

    assignment.deleted_at = current_time
    db.add(assignment)

    await db.commit()


async def update_assignment_status(
    assignment: AppraisalLeadAssignment, new_status: AssignmentStatus, db: AsyncSession
) -> AppraisalLeadAssignment:

    assignment.status = new_status
    db.add(assignment)

    await db.commit()

    await db.refresh(assignment)

    return assignment


async def get_pending_assignments_by_lead_id(
    lead_id: int,
    db: AsyncSession,
):
    stmt = (
        select(
            AppraisalLeadAssignment.id,
            AppraisalLeadAssignment.appraisal_id,
            AppraisalLeadAssignment.lead_id,
            Appraisal.employee_id,
            User.name.label("employee_name"),
            AppraisalLeadAssignment.status,
            AppraisalLeadAssignment.assigned_by,
            AppraisalLeadAssignment.created_at,
            Cycles.start_date,
            Cycles.end_date,
        )
        .select_from(AppraisalLeadAssignment)
        .join(
            Appraisal,
            Appraisal.id == AppraisalLeadAssignment.appraisal_id,
        )
        .join(
            Cycles,
            Cycles.id == Appraisal.cycle_id,
        )
        .join(
            User,
            User.id == Appraisal.employee_id,
        )
        .where(
            AppraisalLeadAssignment.lead_id == lead_id,
            AppraisalLeadAssignment.status == AssignmentStatus.Pending,
            AppraisalLeadAssignment.deleted_at.is_(None),
            Appraisal.deleted_at.is_(None),
            Cycles.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
    )

    result = await db.execute(stmt)
    return result.mappings().all()


async def get_assignments_by_lead_id(
    lead_id: int,
    db: AsyncSession,
):
    stmt = (
        select(
            AppraisalLeadAssignment.id,
            AppraisalLeadAssignment.appraisal_id,
            AppraisalLeadAssignment.lead_id,
            Appraisal.employee_id,
            User.name.label("employee_name"),
            AppraisalLeadAssignment.status,
            AppraisalLeadAssignment.assigned_by,
            AppraisalLeadAssignment.created_at,
            Cycles.start_date,
            Cycles.end_date,
        )
        .select_from(AppraisalLeadAssignment)
        .join(
            Appraisal,
            Appraisal.id == AppraisalLeadAssignment.appraisal_id,
        )
        .join(
            Cycles,
            Cycles.id == Appraisal.cycle_id,
        )
        .join(
            User,
            User.id == Appraisal.employee_id,
        )
        .where(
            AppraisalLeadAssignment.lead_id == lead_id,
            AppraisalLeadAssignment.deleted_at.is_(None),
            Appraisal.deleted_at.is_(None),
            Cycles.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
    )

    result = await db.execute(stmt)
    return result.mappings().all()


async def get_employee_by_mapping_id(
    db: AsyncSession,
    mapping_id: int,
):
    stmt = (
        select(User)
        .join(Appraisal, Appraisal.employee_id == User.id)
        .join(
            AppraisalLeadAssignment,
            AppraisalLeadAssignment.appraisal_id == Appraisal.id,
        )
        .where(AppraisalLeadAssignment.id == mapping_id)
    )

    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise NotFoundException("Employee not found.")

    return employee
