from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class SummaryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    appraisal_id: int
    summary: str = Field(min_length=1)


class SummaryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    summary: str = Field(min_length=1)


class SummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    appraisal_id: int
    summary: str
    created_at: datetime
    updated_at: datetime
