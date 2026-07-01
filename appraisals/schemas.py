from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from models.appraisal import AppraisalStatus
# from models.user import UserRole


class AppraisalCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    cycle_id: int
    employee_id: int

class AppraisalResponse(AppraisalCreate):
    status: AppraisalStatus
    id: int

class IDPCreateUpdate(BaseModel):
    idp_text: str = Field(..., min_length=1, description="The Individual Development Plan text")

class MeetingNotesCreateUpdate(BaseModel):
    meeting_notes: str = Field(..., min_length=1, description="Notes captured by HR during the meeting")

class IDPResponse(BaseModel):
    idp_text: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingNotesResponse(BaseModel):
    message: str
    meeting_notes: str
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingNotesGetResponse(BaseModel):
    meeting_notes: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class CycleDetailSchema(BaseModel):
    cycle_id: int
    cycle_name: str
    start_date: datetime
    end_date: datetime
    cycle_status: datetime

    class Config:
        from_attributes = True

class EmployeeHistoryResponse(BaseModel):
    id: int
    employee_id: int
    status: AppraisalStatus
    idp_text: Optional[str] = None
    meeting_notes: Optional[str] = None
    created_at: datetime
    cycle_details: CycleDetailSchema

    class Config:
        from_attributes = True

class UpdateStatusRequest(BaseModel):
    status: AppraisalStatus

class UpdateStatusResponse(BaseModel):
    message: str
    current_status: AppraisalStatus