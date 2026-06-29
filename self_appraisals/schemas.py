from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SelfAppraisalBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    appraisal_id: int
    accomplishments: str | None = None
    challenges: str | None = None
    career_aspirations: str | None = None

class SelfAppraisalCreate(SelfAppraisalBase):
    pass


class SelfAppraisalUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    accomplishments: str | None = None
    challenges: str | None = None
    career_aspirations: str | None = None


class SelfAppraisalResponse(SelfAppraisalCreate):
    id: int
    created_at: datetime
    updated_at: datetime