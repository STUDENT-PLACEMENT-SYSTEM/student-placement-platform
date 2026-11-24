from backend.app.models.user import User, UserRole
from backend.app.models.student import Student, StudentEmbedding, PlacementStatus
from backend.app.models.recruiter import Recruiter
from backend.app.models.drive import Drive, DriveApplication, DriveStatus, ApplicationStatus
from backend.app.models.placement import PlacementOffer, OfferStatus
from backend.app.models.ml_prediction import MLPrediction, SkillGapRoadmap
from backend.app.models.audit_log import AuditLog

__all__ = [
    "User",
    "UserRole",
    "Student",
    "StudentEmbedding",
    "PlacementStatus",
    "Recruiter",
    "Drive",
    "DriveApplication",
    "DriveStatus",
    "ApplicationStatus",
    "PlacementOffer",
    "OfferStatus",
    "MLPrediction",
    "SkillGapRoadmap",
    "AuditLog"
]
