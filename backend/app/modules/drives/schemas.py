from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import date, datetime

class DriveCreateRequest(BaseModel):
    title: str
    role_name: str
    job_description: str
    min_cgpa: float = 6.00
    max_backlogs: int = 0
    allowed_branches: List[str]
    ctc_min_lpa: float
    ctc_max_lpa: float
    job_location: str
    drive_date: date
    registration_deadline: datetime

class DriveResponse(BaseModel):
    id: uuid.UUID
    recruiter_id: uuid.UUID
    company_name: Optional[str] = None
    title: str
    role_name: str
    job_description: str
    min_cgpa: float
    max_backlogs: int
    allowed_branches: List[str]
    ctc_min_lpa: float
    ctc_max_lpa: float
    job_location: str
    drive_date: date
    registration_deadline: datetime
    status: str

class ApplicationResponse(BaseModel):
    id: uuid.UUID
    drive_id: uuid.UUID
    student_id: uuid.UUID
    status: str
    match_score: Optional[float] = None
    applied_at: datetime
