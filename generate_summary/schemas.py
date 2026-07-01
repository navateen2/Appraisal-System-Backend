from pydantic import BaseModel


class AppraisalSummaryRequest(BaseModel):
    appraisal_id: int


class AppraisalSummaryResponse(BaseModel):
    appraisal_id: int
    summary: str


class CycleSummaryResponse(BaseModel):
    appraisal_id: int
    employee_id: int
    employee_name: str
    summary: str
