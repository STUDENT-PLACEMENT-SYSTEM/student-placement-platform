#!/usr/bin/env python3
"""
CTC Salary Package Regression Training Pipeline.
Trains an XGBoost / GradientBoosting Regressor to predict the placement CTC package (in LPA)
for placed students based on academic performance, coding skills, branch, and experience.
Saves the serialised pipeline artifact to ml/saved_models/ctc_regressor_v1.joblib.
"""

import argparse
import json
import logging
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    import xgboost as xgb
    USE_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor
    USE_XGBOOST = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainCTCRegressor")

NUMERIC_FEATURES = [
    "cgpa",
    "backlogs",
    "history_of_backlogs",
    "internships",
    "projects_count",
    "certifications_count",
    "coding_skills_score",
    "communication_score",
    "aptitude_score",
]

CATEGORICAL_FEATURES = ["gender", "branch"]


def build_preprocessor() -> ColumnTransformer:
    num_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERIC_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def build_model(seed: int = 42):
    if USE_XGBOOST:
        logger.info("Using XGBoost Regressor engine.")
        return xgb.XGBRegressor(
            n_estimators=180,
            learning_rate=0.06,
            max_depth=4,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=3,
            gamma=0.05,
            random_state=seed,
        )
    else:
        logger.info("Using Scikit-Learn GradientBoostingRegressor fallback engine.")
        return GradientBoostingRegressor(
            n_estimators=180,
            learning_rate=0.06,
            max_depth=4,
            subsample=0.85,
            random_state=seed,
        )


def train_ctc_regressor(
    data_path: str,
    output_model_path: str,
    test_size: float = 0.2,
    seed: int = 42,
) -> dict:
    logger.info("Loading dataset from: %s", data_path)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset file not found: {data_path}")

    df = pd.read_csv(data_path)
    logger.info("Dataset loaded successfully with shape: %s", df.shape)

    # Filter strictly for placed students with positive package_lpa
    if "placed" in df.columns:
        placed_df = df[(df["placed"] == 1) & (df["package_lpa"] > 0)].copy()
    else:
        placed_df = df[df["package_lpa"] > 0].copy()

    logger.info("Placed student cohort size: %d records", len(placed_df))
    if len(placed_df) == 0:
        raise ValueError("No placed student records found with package_lpa > 0.")

    # Normalize backlogs column name if active_backlogs is present
    if "active_backlogs" in placed_df.columns and "backlogs" not in placed_df.columns:
        placed_df["backlogs"] = placed_df["active_backlogs"]

    feature_cols = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in placed_df.columns]
    X = placed_df[feature_cols].copy()
    y = placed_df["package_lpa"].astype(float)

    logger.info("Package LPA statistics:\n%s", y.describe().round(2).to_dict())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed
    )
    logger.info("Train set: %d samples, Test set: %d samples", len(X_train), len(X_test))

    preprocessor = build_preprocessor()
    regressor = build_model(seed=seed)

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", regressor),
    ])

    logger.info("Fitting CTC regression pipeline...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    # Clip negative predictions to min baseline
    y_pred = np.clip(y_pred, 3.0, 50.0)

    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(root_mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))
    med_ae = float(median_absolute_error(y_test, y_pred))
    exp_var = float(explained_variance_score(y_test, y_pred))

    # Feature importances
    try:
        cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["ohe"]
        cat_feature_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        all_feature_names = NUMERIC_FEATURES + cat_feature_names

        raw_model = pipeline.named_steps["regressor"]
        importances = raw_model.feature_importances_.tolist()
        feature_importance_dict = dict(sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True))
    except Exception as e:
        logger.warning("Could not extract feature names/importances: %s", e)
        feature_importance_dict = {}

    metrics = {
        "model_type": "XGBRegressor" if USE_XGBOOST else "GradientBoostingRegressor",
        "model_version": "v1.0",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "mae_lpa": round(mae, 4),
        "rmse_lpa": round(rmse, 4),
        "r2_score": round(r2, 4),
        "median_absolute_error_lpa": round(med_ae, 4),
        "explained_variance": round(exp_var, 4),
        "feature_importances": {k: round(v, 4) for k, v in list(feature_importance_dict.items())[:10]},
    }

    print("\n" + "=" * 50)
    print("💰 CTC REGRESSOR EVALUATION METRICS")
    print("=" * 50)
    print(f"Mean Absolute Error (MAE)   : {metrics['mae_lpa']:.4f} LPA")
    print(f"Root Mean Squared Error (RMSE): {metrics['rmse_lpa']:.4f} LPA")
    print(f"R² Score (Variance Explained): {metrics['r2_score']:.4f}")
    print(f"Median Absolute Error        : {metrics['median_absolute_error_lpa']:.4f} LPA")
    print(f"Explained Variance Score     : {metrics['explained_variance']:.4f}")
    print("\nTop Predictors for CTC Package:")
    for feat, imp in list(feature_importance_dict.items())[:8]:
        print(f"  - {feat:25s}: {imp:.4f}")
    print("=" * 50)

    # Attach metadata to pipeline object
    pipeline.model_version_ = "v1.0"
    pipeline.metrics_ = metrics
    pipeline.feature_names_ = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    # Save artifact
    os.makedirs(os.path.dirname(os.path.abspath(output_model_path)), exist_ok=True)
    joblib.dump(pipeline, output_model_path)
    logger.info("Saved trained CTC regressor pipeline to: %s", output_model_path)

    # Save metrics json
    metrics_path = os.path.splitext(output_model_path)[0] + "_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Saved evaluation metrics JSON to: %s", metrics_path)

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train Placement CTC Package Regressor.")
    parser.add_argument(
        "--data-path",
        default="/home/kali/AIML_student_placement/dataset/synthetic_3000_students.csv",
        help="Path to student placement CSV dataset.",
    )
    parser.add_argument(
        "--output-model",
        default="/home/kali/AIML_student_placement/ml/saved_models/ctc_regressor_v1.joblib",
        help="Target output path for serialised pipeline artifact.",
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    train_ctc_regressor(
        data_path=args.data_path,
        output_model_path=args.output_model,
        test_size=args.test_size,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
