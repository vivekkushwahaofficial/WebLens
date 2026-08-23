from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from ml.features.url_features import FEATURE_NAMES as BASE_FEATURE_NAMES
from ml.preprocessing.generate_enhanced_features import (
    COMPONENT_FEATURE_NAMES,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_enhanced_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "ml" / "models"

MODEL_PATH = MODEL_DIR / "weblens_random_forest.joblib"
FEATURE_SCHEMA_PATH = MODEL_DIR / "feature_schema.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.joblib"


FEATURE_NAMES = (
    BASE_FEATURE_NAMES
    + COMPONENT_FEATURE_NAMES
)


def main() -> None:
    """Train the final WebLens Random Forest model."""

    print("=" * 70)
    print("WebLens Final Model Training")
    print("=" * 70)

    # Validate the feature schema.
    if len(FEATURE_NAMES) != 46:
        raise ValueError(
            f"Expected 46 features, found {len(FEATURE_NAMES)}"
        )

    # Load the enhanced feature dataset.
    df = pd.read_csv(DATASET_PATH)

    print(f"\nDataset rows: {len(df):,}")
    print(f"Feature count: {len(FEATURE_NAMES)}")

    # Validate required columns.
    missing_features = [
        feature
        for feature in FEATURE_NAMES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    if "type" not in df.columns:
        raise ValueError("Missing target column: type")

    # Prepare training data.
    X = df[FEATURE_NAMES]
    y = df["type"]

    # Validate data quality.
    if X.isnull().sum().sum() != 0:
        raise ValueError(
            "Training features contain missing values."
        )

    non_numeric = X.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if non_numeric:
        raise ValueError(
            f"Non-numeric features found: {non_numeric}"
        )

    # Train using the configuration validated during evaluation.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    print("\nTraining Random Forest on full dataset...")

    model.fit(X, y)

    # Create model directory.
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save model.
    joblib.dump(
        model,
        MODEL_PATH,
    )

    # Save the exact feature schema.
    joblib.dump(
        FEATURE_NAMES,
        FEATURE_SCHEMA_PATH,
    )

    # Save lightweight model metadata.
    metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "random_state": 42,
        "class_weight": "balanced",
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "classes": model.classes_.tolist(),
        "training_rows": len(df),
    }

    joblib.dump(
        metadata,
        METADATA_PATH,
    )

    print("\nModel training complete.")

    print("\nClasses:")
    print(model.classes_.tolist())

    print("\nSaved artifacts:")
    print(f"Model:          {MODEL_PATH}")
    print(f"Feature schema: {FEATURE_SCHEMA_PATH}")
    print(f"Metadata:       {METADATA_PATH}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
