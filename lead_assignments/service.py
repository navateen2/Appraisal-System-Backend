from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import NotFoundException, BadRequestException
from lead_assignments import repo
from typing import List

async def assign_leads_to_appraisal(appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if not appraisal:
        raise NotFoundException(f"Appraisal cycle tracker with ID {appraisal_id} not found")
        
    if appraisal.status.lower() != "self-appraised":
        raise BadRequestException(
            f"Operation rejected: Assignment requires status 'Self-Appraised', found '{appraisal.status}'"
        )
        
    existing_leads = await repo.get_existing_assigned_lead_ids(appraisal_id, db)
    new_lead_ids = [l_id for l_id in lead_ids if l_id not in existing_leads]
    
    if not new_lead_ids:
        raise BadRequestException("The target checking leads are already registered on this panel")
        
    return await repo.bulk_create_assignments(appraisal_id, new_lead_ids, hr_id, db)

async def get_assigned_leads(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if not appraisal:
        raise NotFoundException(f"Appraisal tracking profile with ID {appraisal_id} not found")
        
    assignments = await repo.get_assigned_leads_with_profiles(appraisal_id, db)
    
    return [
        {
            "mapping_id": entry.id,
            "lead_id": entry.lead_id,
            "name": entry.lead.name if entry.lead else "Unknown Profiles",
            "email": entry.lead.email if entry.lead else "Unknown Email",
            "status": entry.status
        } for entry in assignments
    ]

async def remove_assigned_lead(appraisal_id: int, lead_id: int, db: AsyncSession):
    assignment = await repo.get_assignment_by_composite_key(appraisal_id, lead_id, db)
    if not assignment:
        raise NotFoundException("Target lead assignment mapping not found for this review cycle")
        
    if assignment.appraisal and assignment.appraisal.cycle and assignment.appraisal.cycle.is_closed:
        raise BadRequestException("Modification denied: The root corporate appraisal cycle is closed")

    if assignment.status.value.lower() != "pending":
        raise BadRequestException("Modification denied: Review content has already been officially submitted")
        
    await repo.delete_assignment_cascade(assignment, db)