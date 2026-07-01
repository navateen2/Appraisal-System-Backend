from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from models.cycles import CycleStatus


class CycleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1)
    start_date: datetime
    end_date: datetime
    status: CycleStatus = CycleStatus.Initiated


class CycleUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str | None = Field(None, min_length=1)
    start_date: datetime | None = None
    end_date: datetime | None = None


class CycleStatusUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    status: CycleStatus


class CycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: CycleStatus
    created_by_id: int
    created_at: datetime
    updated_at: datetime


class AssignmentParam(BaseModel):
    model_config = ConfigDict(extra="forbid")
    employee_ids: list[int]


class AppraisalAssignedItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cycle_id: int
    employee_id: int
    status: str


class BulkAssignmentResponse(BaseModel):
    successfully_assigned: list[AppraisalAssignedItem]
    already_assigned_employee_ids: list[int]

class AppraisalsOfCycle(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_name: str
    employee_id: int
    status: str