from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.appraisal import Appraisal
from models.appraisal_lead_assignment import AppraisalLeadAssignment, AssignmentStatus
from models.lead_feedback import LeadFeedback
from typing import List

async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession) -> Appraisal | None:
    stmt = select(Appraisal).where(Appraisal.id == appraisal_id, Appraisal.deleted_at.is_(None))
    res = await db.scalars(stmt)
    return res.first()

async def get_existing_assigned_lead_ids(appraisal_id: int, db: AsyncSession) -> List[int]:
    stmt = select(AppraisalLeadAssignment.lead_id).where(
        AppraisalLeadAssignment.appraisal_id == appraisal_id,
        AppraisalLeadAssignment.deleted_at.is_(None)
    )
    res = await db.scalars(stmt)
    return list(res.all())

async def bulk_create_assignments(appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession) -> List[AppraisalLeadAssignment]:
    created_records = []
    for l_id in lead_ids:
        assignment = AppraisalLeadAssignment(
            appraisal_id=appraisal_id,
            lead_id=l_id,
            assigned_by=hr_id,
            status=AssignmentStatus.Pending
        )
        db.add(assignment)
        created_records.append(assignment)
    await db.commit()
    
    for record in created_records:
        await db.refresh(record)
    return created_records

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

async def get_assignment_by_composite_key(appraisal_id: int, lead_id: int, db: AsyncSession) -> AppraisalLeadAssignment | None:
    stmt = (
        select(AppraisalLeadAssignment)
        .options(selectinload(AppraisalLeadAssignment.appraisal).selectinload(Appraisal.cycle))
        .where(
            AppraisalLeadAssignment.appraisal_id == appraisal_id,
            AppraisalLeadAssignment.lead_id == lead_id,
            AppraisalLeadAssignment.deleted_at.is_(None)
        )
    )
    res = await db.scalars(stmt)
    return res.first()

async def delete_assignment_cascade(assignment: AppraisalLeadAssignment, db: AsyncSession):
    # Cascade atomic clear matching draft entries out of LeadFeedback before dropping the mapping row
    feedback_cleanup_stmt = delete(LeadFeedback).where(LeadFeedback.mapping_id == assignment.id)
    await db.execute(feedback_cleanup_stmt)
    
    await db.delete(assignment)
    await db.commit()