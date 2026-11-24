from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class BranchStat(BaseModel):
    branch: str
    total: int
    placed: int
    percentage: float
    avg_ctc_lpa: float

class KPISummaryResponse(BaseModel):
    total_students: int
    placed_students: int
    placement_percentage: float
    average_ctc_lpa: float
    median_ctc_lpa: float
    highest_ctc_lpa: float
    total_offers: int
    branch_breakdown: List[BranchStat]
    recent_activity: Optional[dict[str, Any]] = None
