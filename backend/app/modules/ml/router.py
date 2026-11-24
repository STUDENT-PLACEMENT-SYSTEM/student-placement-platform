from fastapi import APIRouter
from backend.app.modules.ml.schemas import MLInferenceRequest, PlacementPredictionResponse
from backend.app.modules.ml.service import predict_student_placement

router = APIRouter(prefix="/ml", tags=["Machine Learning Inference"])

@router.post("/predict-placement", response_model=PlacementPredictionResponse)
async def predict_placement(data: MLInferenceRequest):
    return predict_student_placement(data)
