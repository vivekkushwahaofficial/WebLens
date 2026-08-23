from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ml.features.url_features import FEATURE_NAMES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_features.csv"
)


def evaluate_model(name, model, x_train, x_test, y_train, y_test):
    """Train and evaluate one baseline model."""

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    print(f"\nAccuracy: {accuracy_score(y_test, predictions):.4f}")

    print(
        f"Macro Precision: "
        f"{precision_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        f"Macro Recall: "
        f"{recall_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        f"Macro F1: "
        f"{f1_score(y_test, predictions, average='macro'):.4f}"
    )

    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))


def main() -> None:
    """Train initial URL classification baselines."""

    print("=" * 70)
    print("WebLens Baseline Model Training")
    print("=" * 70)

    # Load generated feature dataset.
    df = pd.read_csv(DATASET_PATH)

    print(f"\nDataset rows: {len(df):,}")

    # Use the canonical feature schema shared by training and inference.
    missing_features = [
        name for name in FEATURE_NAMES
        if name not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    feature_columns = FEATURE_NAMES

    print(f"Feature count: {len(feature_columns)}")

    X = df[feature_columns]
    y = df["type"]

    # Random stratified URL-level split.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows: {len(X_test):,}")

    # ---------------------------------------------------------
    # Logistic Regression
    # ---------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logistic_regression = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )

    evaluate_model(
        "Logistic Regression",
        logistic_regression,
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
    )

    # ---------------------------------------------------------
    # Random Forest
    # ---------------------------------------------------------

    random_forest = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    evaluate_model(
        "Random Forest",
        random_forest,
        X_train,
        X_test,
        y_train,
        y_test,
    )


if __name__ == "__main__":
    main()
