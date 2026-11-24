from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime

class StudentProfileResponse(BaseModel):
    id: uuid.UUID
    roll_number: str
    full_name: str
    branch: str
    batch_year: int
    cgpa: float
    active_backlogs: int
    history_of_backlogs: int
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_s3_key: Optional[str] = None
    parsed_resume: Optional[dict[str, Any]] = None
    placement_status: str
    is_eligible_for_placements: bool

class StudentUpdateRequest(BaseModel):
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

class ResumeUploadResponse(BaseModel):
    status: str
    s3_key: str
    message: str
