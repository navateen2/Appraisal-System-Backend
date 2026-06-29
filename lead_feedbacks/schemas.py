from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from models.appraisal_lead_assignment import AssignmentStatus

class FeedbackItemBase(BaseModel):
    competency_id: int
    score: int = Field(..., ge=1, le=10, description="Score must be between 1 and 10")
    strengths: Optional[str] = None
    improvements: Optional[str] = None

class CreateFeedbackItemRequest(FeedbackItemBase):
    pass

class CreateFeedbackFormPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    items: List[CreateFeedbackItemRequest]

class UpdateFeedbackItemRequest(FeedbackItemBase):
    pass

class UpdateFeedbackFormPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    items: List[UpdateFeedbackItemRequest]

class FeedbackItemResponse(BaseModel):
    id: int
    competency_id: int
    competency_name: str
    score: int
    strengths: Optional[str]
    improvements: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class FeedbackFormResponse(BaseModel):
    mapping_id: int
    lead_id: int
    appraisal_id: int
    status: AssignmentStatus
    feedbacks: List[FeedbackItemResponse]