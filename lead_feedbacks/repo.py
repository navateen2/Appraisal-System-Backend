from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.appraisal_lead_assignment import AppraisalLeadAssignment
from models.lead_feedback import LeadFeedback
from lead_feedbacks.schemas import CreateFeedbackItemRequest, UpdateFeedbackItemRequest
from typing import List

async def get_assignment_by_id(mapping_id: int, db: AsyncSession) -> AppraisalLeadAssignment | None:
    stmt = (
    select(AppraisalLeadAssignment)
    .where(
        AppraisalLeadAssignment.id == mapping_id,
        AppraisalLeadAssignment.deleted_at.is_(None)
    )
)
    res = await db.scalars(stmt)
    return res.first()

async def get_feedbacks_by_mapping_id(mapping_id: int, db: AsyncSession) -> List[LeadFeedback]:
    stmt = (
        select(LeadFeedback)
        .options(selectinload(LeadFeedback.competency))
        .where(LeadFeedback.mapping_id == mapping_id)
    )
    res = await db.scalars(stmt)
    return res.all()

async def bulk_create_feedbacks(mapping_id: int, items: List[CreateFeedbackItemRequest], db: AsyncSession):
    for item in items:
        db_item = LeadFeedback(
            mapping_id=mapping_id,
            competency_id=item.competency_id,
            score=item.score,
            strengths=item.strengths,
            improvements=item.improvements
        )
        db.add(db_item)
    await db.commit()

async def update_or_insert_feedback_item(mapping_id: int, item: UpdateFeedbackItemRequest, db: AsyncSession):
    stmt = select(LeadFeedback).where(
        LeadFeedback.mapping_id == mapping_id, 
        LeadFeedback.competency_id == item.competency_id
    )
    res = await db.scalars(stmt)
    db_item = res.first()
    
    if db_item:
        db_item.score = item.score
        db_item.strengths = item.strengths
        db_item.improvements = item.improvements
    else:
        db_item = LeadFeedback(
            mapping_id=mapping_id,
            competency_id=item.competency_id,
            score=item.score,
            strengths=item.strengths,
            improvements=item.improvements
        )
        db.add(db_item)
        
    await db.commit()