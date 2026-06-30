import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.appraisal import Appraisal, AppraisalStatus
from models.appraisal_lead_assignment import AppraisalLeadAssignment, AssignmentStatus
from models.lead_feedback import LeadFeedback
from models.associations import employee_lead_recommendations
from typing import List

async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession) -> Appraisal | None:
    stmt = select(Appraisal).where(Appraisal.id == appraisal_id, Appraisal.deleted_at.is_(None))
    res = await db.scalars(stmt)
    return res.first()

async def get_assignment_by_id(mapping_id: int, db: AsyncSession) -> AppraisalLeadAssignment | None:
    stmt = (
        select(AppraisalLeadAssignment)
        .options(selectinload(AppraisalLeadAssignment.appraisal))
        .where(
            AppraisalLeadAssignment.id == mapping_id,
            AppraisalLeadAssignment.deleted_at.is_(None)
        )
    )
    res = await db.scalars(stmt)
    return res.first()

async def get_existing_assigned_lead_ids(appraisal_id: int, db: AsyncSession) -> List[int]:
    stmt = select(AppraisalLeadAssignment.lead_id).where(
        AppraisalLeadAssignment.appraisal_id == appraisal_id,
        AppraisalLeadAssignment.deleted_at.is_(None)
    )
    res = await db.scalars(stmt)
    return list(res.all())

async def get_recommended_lead_ids(appraisal_id: int, db: AsyncSession) -> List[int]:
    stmt = select(employee_lead_recommendations.c.recommended_lead_id).where(
        employee_lead_recommendations.c.appraisal_id == appraisal_id
    )
    res = await db.scalars(stmt)
    return list(res.all())

async def bulk_create_assignments(appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession) -> List[AppraisalLeadAssignment]:
    for l_id in lead_ids:
        assignment = AppraisalLeadAssignment(
            appraisal_id=appraisal_id,
            lead_id=l_id,
            assigned_by=hr_id,
            status=AssignmentStatus.Pending
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
        .where(
            AppraisalLeadAssignment.appraisal_id == appraisal_id,
            AppraisalLeadAssignment.deleted_at.is_(None)
        )
    )
    res = await db.scalars(stmt)
    return list(res.all())

async def delete_assignment_cascade(assignment: AppraisalLeadAssignment, db: AsyncSession):
    current_time = datetime.utcnow()

    feedback_cleanup_stmt = (
        update(LeadFeedback)
        .where(
            LeadFeedback.mapping_id == assignment.id,
            LeadFeedback.deleted_at.is_(None)
        )
        .values(deleted_at=current_time)
    )
    await db.execute(feedback_cleanup_stmt)
    
    assignment.deleted_at = current_time
    db.add(assignment)
    
    await db.commit()

async def update_assignment_status(
    assignment: AppraisalLeadAssignment, 
    new_status: AssignmentStatus, 
    db: AsyncSession
) -> AppraisalLeadAssignment:
    
    assignment.status = new_status
    db.add(assignment) 
    
    await db.commit()
    
    await db.refresh(assignment)
    
    return assignment

async def get_pending_assignments_by_lead_id(lead_id: int, db: AsyncSession) -> List[AppraisalLeadAssignment]:
    stmt = (
        select(AppraisalLeadAssignment)
        .join(AppraisalLeadAssignment.appraisal) 
        .where(
            AppraisalLeadAssignment.lead_id == lead_id,
            AppraisalLeadAssignment.status == AssignmentStatus.Pending,
            AppraisalLeadAssignment.deleted_at.is_(None),
            Appraisal.status == AppraisalStatus.InitiateFeedback,
            Appraisal.deleted_at.is_(None)
        )
    )
    res = await db.scalars(stmt)
    return list(res.all())