from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import datetime, date
from models.appraisal_lead_assignment import AssignmentStatus


class AssignLeadsRequest(BaseModel):
    lead_ids: List[int] = Field(..., min_items=1, description="List of unique checking Lead IDs")


class LeadAssignmentResponse(BaseModel):
    id: int
    appraisal_id: int
    lead_id: int
    assigned_by: int
    employee_id: int
    employee_name: str
    status: AssignmentStatus
    created_at: datetime
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)


class AssignedLeadProfileResponse(BaseModel):
    mapping_id: int
    appraisal_id: int
    lead_id: int
    name: str
    status: AssignmentStatus

    model_config = ConfigDict(from_attributes=True)


class SubmitFeedbackResponse(BaseModel):
    mapping_id: int
    appraisal_id: int
    lead_id: int
    status: AssignmentStatus
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
