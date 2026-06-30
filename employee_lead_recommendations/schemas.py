from pydantic import BaseModel, EmailStr, Field



class LeadRecommendationRequest(BaseModel):
    recommended_lead_ids: list[int] = Field(
        min_length=1,
        description="List of employee IDs of recommended leads"
    )



class LeadRecommendationResponse(BaseModel):
    status: str
    recommended_lead_ids: list[int]



class RecommendedLead(BaseModel):
    recommended_lead_id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class LeadRecommendationListResponse(BaseModel):
    recommendations: list[RecommendedLead]