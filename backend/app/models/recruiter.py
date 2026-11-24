import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(150), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    company_logo_url = Column(String(500), nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="recruiter_profile")
    drives = relationship("Drive", back_populates="recruiter", cascade="all, delete-orphan")
