import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    placement_probability = Column(Numeric(5, 2), nullable=False)
    predicted_ctc_min = Column(Numeric(6, 2), nullable=False)
    predicted_ctc_max = Column(Numeric(6, 2), nullable=False)
    predicted_ctc_median = Column(Numeric(6, 2), nullable=False)
    top_features = Column(JSONB, default=dict, nullable=False)
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="predictions")

class SkillGapRoadmap(Base):
    __tablename__ = "skill_gap_roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    target_drive_id = Column(UUID(as_uuid=True), ForeignKey("drives.id", ondelete="SET NULL"), nullable=True)
    target_role = Column(String(150), nullable=False)
    missing_skills = Column(ARRAY(String), nullable=False)
    recommended_projects = Column(JSONB, default=list, nullable=False)
    weekly_roadmap = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="roadmaps")
