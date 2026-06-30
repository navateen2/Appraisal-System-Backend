from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import datetime
from models.appraisal_lead_assignment import AssignmentStatus

class AssignLeadsRequest(BaseModel):
    lead_ids: List[int] = Field(..., min_items=1, description="List of unique checking Lead IDs")

class LeadAssignmentResponse(BaseModel):
    id: int
    appraisal_id: int
    lead_id: int
    assigned_by: int
    status: AssignmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignedLeadProfileResponse(BaseModel):
    mapping_id: int
    appraisal_id: int
    lead_id: int
    name: str
    status: AssignmentStatus

    model_config = ConfigDict(from_attributes=True)