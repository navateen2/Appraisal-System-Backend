from pydantic import BaseModel


class AppraisalSummaryRequest(BaseModel):
    appraisal_id: int


class AppraisalSummaryResponse(BaseModel):
    appraisal_id: int
    summary: str
