#!/usr/bin/env python3
"""
Placement Classification Training Pipeline.
Trains an XGBoost / GradientBoosting Classifier to predict student placement status (0 or 1)
and placement probability based on academic, technical, and extracurricular features.
Saves the serialised pipeline artifact to ml/saved_models/placement_classifier_v1.joblib.
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
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    import xgboost as xgb
    USE_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    USE_XGBOOST = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainPlacementClassifier")

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
        logger.info("Using XGBoost Classifier engine.")
        return xgb.XGBClassifier(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=4,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=2,
            gamma=0.1,
            random_state=seed,
            eval_metric="logloss",
        )
    else:
        logger.info("Using Scikit-Learn GradientBoostingClassifier fallback engine.")
        return GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=4,
            subsample=0.85,
            random_state=seed,
        )


def train_placement_classifier(
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

    # Normalize backlogs column name if active_backlogs is present
    if "active_backlogs" in df.columns and "backlogs" not in df.columns:
        df["backlogs"] = df["active_backlogs"]

    # Validate target presence
    if "placed" not in df.columns:
        raise ValueError("Target column 'placed' not found in dataset.")

    feature_cols = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in df.columns]
    X = df[feature_cols].copy()
    y = df["placed"].astype(int)

    logger.info("Class distribution: \n%s", y.value_counts(normalize=True).to_dict())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    logger.info("Train set: %d samples, Test set: %d samples", len(X_train), len(X_test))

    preprocessor = build_preprocessor()
    classifier = build_model(seed=seed)

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    logger.info("Fitting placement classification pipeline...")
    pipeline.fit(X_train, y_train)

    # Predict & evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature importances
    try:
        cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["ohe"]
        cat_feature_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        all_feature_names = NUMERIC_FEATURES + cat_feature_names
        
        raw_model = pipeline.named_steps["classifier"]
        importances = raw_model.feature_importances_.tolist()
        feature_importance_dict = dict(sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True))
    except Exception as e:
        logger.warning("Could not extract feature names/importances: %s", e)
        feature_importance_dict = {}

    metrics = {
        "model_type": "XGBClassifier" if USE_XGBOOST else "GradientBoostingClassifier",
        "model_version": "v1.0",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(acc, 4),
        "roc_auc": round(roc_auc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "feature_importances": {k: round(v, 4) for k, v in list(feature_importance_dict.items())[:10]},
    }

    print("\n" + "=" * 50)
    print("🎯 PLACEMENT CLASSIFIER EVALUATION METRICS")
    print("=" * 50)
    print(f"Accuracy  : {metrics['accuracy']:.4f}")
    print(f"ROC-AUC   : {metrics['roc_auc']:.4f}")
    print(f"Precision : {metrics['precision']:.4f}")
    print(f"Recall    : {metrics['recall']:.4f}")
    print(f"F1 Score  : {metrics['f1_score']:.4f}")
    print("\nConfusion Matrix [TN, FP], [FN, TP]:")
    print(f"{cm}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, digits=4))
    print("Top Influencing Features:")
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
    logger.info("Saved trained placement classifier pipeline to: %s", output_model_path)

    # Save metrics json
    metrics_path = os.path.splitext(output_model_path)[0] + "_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Saved evaluation metrics JSON to: %s", metrics_path)

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train Placement Status & Probability Classifier.")
    parser.add_argument(
        "--data-path",
        default="/home/kali/AIML_student_placement/dataset/synthetic_3000_students.csv",
        help="Path to synthetic or college student CSV dataset.",
    )
    parser.add_argument(
        "--output-model",
        default="/home/kali/AIML_student_placement/ml/saved_models/placement_classifier_v1.joblib",
        help="Target output path for serialised pipeline artifact.",
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    train_placement_classifier(
        data_path=args.data_path,
        output_model_path=args.output_model,
        test_size=args.test_size,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
