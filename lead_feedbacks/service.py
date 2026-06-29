from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import NotFoundException, BadRequestException, ForbiddenException
from models.appraisal_lead_assignment import AssignmentStatus
from models.user import UserRole
from lead_feedbacks import repo
from lead_feedbacks.schemas import CreateFeedbackItemRequest, UpdateFeedbackItemRequest
from typing import List

async def _validate_assignment_for_mutation(mapping_id: int, lead_id: int, db: AsyncSession):
    assignment = await repo.get_assignment_by_id(mapping_id, db)
    if not assignment:
        raise NotFoundException(f"Assignment mapping with id {mapping_id} not found")
    
    if assignment.lead_id != lead_id:
        raise ForbiddenException("You are not officially assigned to handle this appraisal form")
        
    if assignment.status == AssignmentStatus.Submitted:
        raise BadRequestException("Cannot modify feedback forms once they have been officially submitted")
    return assignment

async def save_feedback_form(mapping_id: int, items: List[CreateFeedbackItemRequest], lead_id: int, db: AsyncSession):
    await _validate_assignment_for_mutation(mapping_id, lead_id, db)
    
    existing = await repo.get_feedbacks_by_mapping_id(mapping_id, db)
    if existing:
        raise BadRequestException("Feedback form already initialized for this mapping. Use PUT to modify drafts.")
        
    await repo.bulk_create_feedbacks(mapping_id, items, db)
    return await get_feedback_form(mapping_id, lead_id, UserRole.Employee, db)

async def update_feedback_form(mapping_id: int, items: List[UpdateFeedbackItemRequest], lead_id: int, db: AsyncSession):
    await _validate_assignment_for_mutation(mapping_id, lead_id, db)
    
    for item in items:
        await repo.update_or_insert_feedback_item(mapping_id, item, db)
        
    return await get_feedback_form(mapping_id, lead_id, UserRole.Employee, db)

async def get_feedback_form(mapping_id: int, user_id: int, user_role: str, db: AsyncSession):
    assignment = await repo.get_assignment_by_id(mapping_id, db)
    if not assignment:
        raise NotFoundException(f"Assignment mapping with id {mapping_id} not found")
    
    if user_role == UserRole.Employee and assignment.lead_id != user_id:
        raise ForbiddenException("Access to view this individual draft form payload is restricted")
        
    feedbacks = await repo.get_feedbacks_by_mapping_id(mapping_id, db)
    
    formatted_items = [
        {
            "id": f.id,
            "competency_id": f.competency_id,
            "competency_name": f.competency.name,
            "score": f.score,
            "strengths": f.strengths,
            "improvements": f.improvements
        } for f in feedbacks
    ]
    
    return {
        "mapping_id": mapping_id,
        "lead_id" : assignment.lead_id,
        "appraisal_id" : assignment.appraisal_id,
        "status": assignment.status,
        "feedbacks": formatted_items
    }