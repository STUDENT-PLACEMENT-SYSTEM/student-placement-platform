import os
import joblib
import numpy as np
import pandas as pd
from backend.app.modules.ml.schemas import MLInferenceRequest, PlacementPredictionResponse

MODEL_DIR = "/home/kali/AIML_student_placement/ml/saved_models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "placement_classifier_v1.joblib")
REGRESSOR_PATH = os.path.join(MODEL_DIR, "ctc_regressor_v1.joblib")

_classifier = None
_regressor = None

def get_models():
    global _classifier, _regressor
    if _classifier is None and os.path.exists(CLASSIFIER_PATH):
        try:
            _classifier = joblib.load(CLASSIFIER_PATH)
        except Exception:
            _classifier = None
    if _regressor is None and os.path.exists(REGRESSOR_PATH):
        try:
            _regressor = joblib.load(REGRESSOR_PATH)
        except Exception:
            _regressor = None
    return _classifier, _regressor

def predict_student_placement(data: MLInferenceRequest) -> PlacementPredictionResponse:
    clf, reg = get_models()

    if clf is not None and reg is not None:
        input_df = pd.DataFrame([{
            "cgpa": data.cgpa,
            "branch": data.branch,
            "backlogs": data.backlogs,
            "history_of_backlogs": data.history_of_backlogs,
            "internships": data.internships,
            "projects_count": data.projects_count,
            "certifications_count": getattr(data, "certifications_count", 1),
            "coding_skills_score": data.coding_skills_score,
            "communication_score": data.communication_score,
            "aptitude_score": data.aptitude_score,
            "gender": getattr(data, "gender", "Male"),
        }])

        prob_raw = float(clf.predict_proba(input_df)[0, 1]) * 100.0
        prob = round(float(np.clip(prob_raw, 0.0, 100.0)), 1)

        pred_ctc = float(reg.predict(input_df)[0])
        pred_ctc = max(3.5, pred_ctc)
        median_ctc = round(pred_ctc, 1)
        min_ctc = max(3.5, round(median_ctc * 0.85, 1))
        max_ctc = round(median_ctc * 1.30, 1)

        version = getattr(clf, "model_version_", "xgboost_v1.0")
    else:
        # Fallback heuristic calculation matching calibrated Indian placement statistics
        base_score = (
            (data.cgpa / 10.0) * 0.35 +
            (min(data.internships, 3) / 3.0) * 0.25 +
            (data.coding_skills_score / 10.0) * 0.20 +
            (data.communication_score / 10.0) * 0.10 +
            (data.aptitude_score / 100.0) * 0.10
        ) * 100.0

        penalty = (data.backlogs * 18.0) + (data.history_of_backlogs * 4.0)
        prob = max(1.0, min(99.0, round(base_score - penalty, 1)))

        min_ctc = max(3.5, round(data.cgpa * 0.7 + data.internships * 1.2, 1))
        median_ctc = round(min_ctc * 1.35, 1)
        max_ctc = round(median_ctc * 1.6, 1)
        version = "heuristic_fallback_v1.0"

    if prob >= 75.0:
        tier = "High Probability"
    elif prob >= 45.0:
        tier = "Moderate Probability"
    else:
        tier = "Needs Skill Acceleration"

    factors = [
        {"feature": "Active Backlogs", "impact": "Clear" if data.backlogs == 0 else f"High Risk ({data.backlogs})", "value": data.backlogs},
        {"feature": "CGPA", "impact": "Positive" if data.cgpa >= 7.5 else "Needs Improvement", "value": data.cgpa},
        {"feature": "Coding & DSA Score", "impact": "Strong" if data.coding_skills_score >= 7.0 else "Focus Area", "value": f"{data.coding_skills_score}/10"},
        {"feature": "Internships", "impact": "Positive" if data.internships >= 1 else "None Recorded", "value": data.internships},
    ]

    return PlacementPredictionResponse(
        placement_probability=prob,
        placement_tier=tier,
        predicted_ctc_min_lpa=min_ctc,
        predicted_ctc_median_lpa=median_ctc,
        predicted_ctc_max_lpa=max_ctc,
        top_factors=factors,
        model_version=version
    )
