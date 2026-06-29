from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
# from models.user import UserRole


class AppraisalCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    cycle_id: int
    employee_id: int
    status: str =Field(min_length=1,max_length=10)
    idp_text: str = Field(min_length=1,max_length=200)
    hr_notes:str = Field(min_length=1,max_length=200)

class AppraisalUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    status: str =Field(min_length=1,max_length=10)
    idp_text: str = Field(min_length=1,max_length=200)
    hr_notes:str = Field(min_length=1,max_length=200)


class AppraisalResponse(AppraisalCreate):
    id: int
    



class AppraisalResponseId(AppraisalResponse):
    created_at: datetime
    updated_at: datetime
