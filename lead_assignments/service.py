from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import NotFoundException, BadRequestException
from lead_assignments import repo
from typing import List
from models.appraisal import AppraisalStatus
from models.appraisal_lead_assignment import AssignmentStatus

async def assign_leads_to_appraisal(appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if not appraisal:
        raise NotFoundException(f"Appraisal cycle tracker with ID {appraisal_id} not found")
        
    if appraisal.status!=AppraisalStatus.SelfAppraised:
        raise BadRequestException(
            f"Operation rejected: Assignment requires status 'Self-Appraised', found '{appraisal.status}'"
        )
    
    recommended_leads = await repo.get_recommended_lead_ids(appraisal_id, db) 
    invalid_leads = [l_id for l_id in lead_ids if l_id not in recommended_leads]
    if invalid_leads:
        raise BadRequestException(
            f"Operation rejected: The following Lead IDs were not recommended by the employee "
            f"during their self-appraisal stage: {invalid_leads}"
        )
        
    existing_leads = await repo.get_existing_assigned_lead_ids(appraisal_id, db)
    new_lead_ids = [l_id for l_id in lead_ids if l_id not in existing_leads]
    
    if not new_lead_ids:
        raise BadRequestException("All Leads were already assigned")
        
    return await repo.bulk_create_assignments(appraisal_id, new_lead_ids, hr_id, db)

async def get_assigned_leads(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if not appraisal:
        raise NotFoundException(f"Appraisal tracking profile with ID {appraisal_id} not found")
        
    assignments = await repo.get_assigned_leads_with_profiles(appraisal_id, db)
    
    return [
        {
            "mapping_id": entry.id,
            "appraisal_id": appraisal_id,
            "lead_id": entry.lead_id,
            "name": entry.lead.name if entry.lead else "Unknown Profiles",
            "status": entry.status
        } for entry in assignments
    ]

async def remove_assigned_lead(appraisal_id: int, lead_id: int, db: AsyncSession):
    assignment = await repo.get_assignment_by_composite_key(appraisal_id, lead_id, db)
    if not assignment:
        raise NotFoundException("Target lead assignment mapping not found for this review cycle")

    if assignment.status != AssignmentStatus.Pending:
        raise BadRequestException("Modification denied: Lead feedback already submitted")
    
    if assignment.appraisal is None or assignment.appraisal.deleted_at is not None:
        raise NotFoundException("Modification denied: The associated appraisal has been soft-deleted or does not exist")

    if assignment.appraisal.status != AppraisalStatus.InitiateFeedback:
        raise BadRequestException(
            f"Modification denied: Assignments can only be removed while appraisal status is 'Initiate Feedback'. "
            f"Current status is '{assignment.appraisal.status}'"
        )
        
    await repo.delete_assignment_cascade(assignment, db)