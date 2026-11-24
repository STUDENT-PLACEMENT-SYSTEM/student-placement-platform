from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MLInferenceRequest(BaseModel):
    cgpa: float
    branch: str
    backlogs: int = 0
    history_of_backlogs: int = 0
    internships: int = 0
    projects_count: int = 2
    coding_skills_score: float = 7.0
    communication_score: float = 7.0
    aptitude_score: float = 70.0

class PlacementPredictionResponse(BaseModel):
    placement_probability: float
    placement_tier: str
    predicted_ctc_min_lpa: float
    predicted_ctc_median_lpa: float
    predicted_ctc_max_lpa: float
    top_factors: List[Dict[str, Any]]
    model_version: str
