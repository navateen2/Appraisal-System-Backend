import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import ForbiddenException, NotFoundException, BadRequestException
from lead_assignments import repo
from typing import List
from models.appraisal import AppraisalStatus
from models.appraisal_lead_assignment import AssignmentStatus


async def assign_leads_to_appraisal(appraisal_id: int, lead_ids: List[int], hr_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if not appraisal:
        raise NotFoundException(f"Appraisal cycle tracker with ID {appraisal_id} not found")

    recommended_leads = await repo.get_recommended_lead_ids(appraisal_id, db)

    input_leads_set = set(lead_ids)

    if appraisal.status == AppraisalStatus.SelfAppraised:
        existing_leads = await repo.get_existing_assigned_lead_ids(appraisal_id, db)
        if existing_leads:
            raise BadRequestException(
                "Initial assignment already exists. Use 'FeedbackInitiated' state to append leads."
            )
        new_lead_ids = lead_ids

    elif appraisal.status == AppraisalStatus.InitiateFeedback:
        existing_leads = await repo.get_existing_assigned_lead_ids(appraisal_id, db)

        missing_from_payload = [l_id for l_id in existing_leads if l_id not in input_leads_set]
        if missing_from_payload:
            raise BadRequestException(
                f"Operation rejected: Assigned lead already in database missing in input lead_ids list"
                f"Missing Lead IDs: {missing_from_payload}"
            )

        new_lead_ids = [l_id for l_id in lead_ids if l_id not in existing_leads]

        if not new_lead_ids:
            raise BadRequestException("No new leads were added to the database; all are already assigned.")

    else:
        raise BadRequestException(
            f"Operation rejected: Current status '{appraisal.status}' does not allow lead assignments."
        )

    invalid_leads = [l_id for l_id in new_lead_ids if l_id not in recommended_leads]
    if invalid_leads:
        raise BadRequestException(
            f"Operation rejected: The following new Lead IDs were not recommended by the employee "
            f"during their self-appraisal stage: {invalid_leads}"
        )

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
            "status": entry.status,
        }
        for entry in assignments
    ]


async def remove_assigned_lead(mapping_id: int, db: AsyncSession):
    assignment = await repo.get_assignment_by_id(mapping_id, db)
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


async def submit_lead_feedback(mapping_id: int, current_user_id: int, db: AsyncSession):
    assignment = await repo.get_assignment_by_id(mapping_id, db)
    if not assignment:
        raise NotFoundException(f"Active assignment record with ID {mapping_id} not found")
    if assignment.lead_id != current_user_id:
        raise ForbiddenException("Access denied: You are not authorized to submit feedback for this assignment.")
    if assignment.status == AssignmentStatus.Submitted:
        raise BadRequestException("Operation rejected: Feedback has already been submitted.")
    elif assignment.status != AssignmentStatus.Pending:
        raise BadRequestException(f"Operation rejected: Cannot submit feedback with status '{assignment.status}'")

    if (
        assignment.appraisal is None
        or assignment.appraisal.deleted_at is not None
        or assignment.appraisal.status != AppraisalStatus.InitiateFeedback
    ):
        raise NotFoundException(
            "Operation rejected: The associated appraisal lifecycle does not exist or has been deleted or appraisal status not Initiate Feedback"
        )

    updated_assignment = await repo.update_assignment_status(assignment, AssignmentStatus.Submitted, db)

    return {
        "mapping_id": updated_assignment.id,
        "appraisal_id": updated_assignment.appraisal_id,
        "lead_id": updated_assignment.lead_id,
        "status": updated_assignment.status,
        "updated_at": datetime.utcnow(),
    }


async def get_pending_assignments_for_lead(lead_id: int, current_user_id: int, db: AsyncSession):
    if lead_id != current_user_id:
        raise ForbiddenException("Access denied: You cannot view pending assignments for another user.")

    assignments = await repo.get_pending_assignments_by_lead_id(lead_id, db)

    return [
        {
            "id": entry.id,
            "appraisal_id": entry.appraisal_id,
            "lead_id": entry.lead_id,
            "assigned_by": entry.assigned_by,
            "status": entry.status,
            "created_at": entry.created_at,
        }
        for entry in assignments
    ]
