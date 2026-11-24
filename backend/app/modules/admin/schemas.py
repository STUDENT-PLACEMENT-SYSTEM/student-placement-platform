from pydantic import BaseModel
from typing import Optional, Any, List
import uuid
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    entity_name: str
    entity_id: Optional[uuid.UUID] = None
    details: dict[str, Any]
    created_at: datetime

class PendingRecruiterResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    contact_person: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
