from pydantic import BaseModel, ConfigDict

class CompetenciesResponse(BaseModel):
    id: int
    name: str

class CreateCompetenciesRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    name: str