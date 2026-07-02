from typing import List, Optional

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

class CompetencyFeedbackResponse(BaseModel):
    competency_name: Optional[str]
    score: Optional[int]
    strengths: Optional[str]
    improvements: Optional[str]


class LeadFeedbackResponse(BaseModel):
    assignment_id: Optional[int]
    lead_id: Optional[int]
    lead_name: Optional[str]
    feedback: List[CompetencyFeedbackResponse]


class AppraisalSummaryDataResponse(BaseModel):
    appraisal_id: int
    cycle_id: Optional[int]
    cycle_name: Optional[str]

    employee_id: Optional[int]
    employee_name: Optional[str]

    hr_notes: Optional[str]
    idp_text: Optional[str]

    self_appraisal_id: Optional[int]
    accomplishments: Optional[str]
    challenges: Optional[str]
    career_aspirations: Optional[str]

    lead_feedback: List[LeadFeedbackResponse]