from pydantic import BaseModel
from typing import Optional
import uuid

class MarkPlacedRequest(BaseModel):
    student_id: uuid.UUID
    company_name: str
    ctc_lpa: float
    drive_id: Optional[uuid.UUID] = None
    is_on_campus: bool = True

class MarkPlacedResponse(BaseModel):
    success: bool
    offer_id: uuid.UUID
    student_id: uuid.UUID
    company_name: str
    ctc_lpa: float
    message: str

class DriveApprovalRequest(BaseModel):
    is_approved: bool
    feedback: Optional[str] = None
