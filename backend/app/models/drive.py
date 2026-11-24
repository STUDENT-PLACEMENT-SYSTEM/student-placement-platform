import uuid
import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Integer, Numeric, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from backend.app.core.database import Base

class DriveStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFERED = "offered"
    REJECTED = "rejected"

class Drive(Base):
    __tablename__ = "drives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    role_name = Column(String(150), nullable=False)
    job_description = Column(Text, nullable=False)
    jd_embedding = Column(Vector(1536), nullable=True)
    min_cgpa = Column(Numeric(4, 2), default=6.00, nullable=False)
    max_backlogs = Column(Integer, default=0, nullable=False)
    allowed_branches = Column(ARRAY(String), nullable=False)
    ctc_min_lpa = Column(Numeric(6, 2), nullable=False)
    ctc_max_lpa = Column(Numeric(6, 2), nullable=False)
    job_location = Column(String(150), nullable=False)
    drive_date = Column(Date, nullable=False)
    registration_deadline = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(
        Enum(DriveStatus, name="drive_status_enum", create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        default=DriveStatus.DRAFT,
        nullable=False,
        index=True
    )
    approved_by_tpo_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    recruiter = relationship("Recruiter", back_populates="drives")
    applications = relationship("DriveApplication", back_populates="drive", cascade="all, delete-orphan")
    offers = relationship("PlacementOffer", back_populates="drive")

class DriveApplication(Base):
    __tablename__ = "drive_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_id = Column(UUID(as_uuid=True), ForeignKey("drives.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        Enum(ApplicationStatus, name="application_status_enum", create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        default=ApplicationStatus.APPLIED,
        nullable=False,
        index=True
    )
    match_score = Column(Numeric(5, 2), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    drive = relationship("Drive", back_populates="applications")
    student = relationship("Student", back_populates="applications")
