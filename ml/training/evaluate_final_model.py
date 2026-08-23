from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from ml.preprocessing.generate_enhanced_features import FEATURE_NAMES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_enhanced_features.csv"
)


def extract_hostname(url: str) -> str:
    """Extract a normalized hostname."""

    url = str(url).strip()

    if not url:
        return ""

    if "://" not in url:
        url = "//" + url

    try:
        parsed = urlparse(url)
        return (parsed.hostname or "").lower()
    except ValueError:
        return ""


def main() -> None:
    """Perform the final strict unseen-domain evaluation."""

    print("=" * 70)
    print("WebLens Final Model Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nDataset rows: {len(df):,}")
    print(f"Feature count: {len(FEATURE_NAMES)}")

    # Extract hostnames for domain-disjoint evaluation.
    df["hostname"] = df["url"].apply(extract_hostname)

    hostname_class_counts = (
        df.groupby("hostname")["type"]
        .nunique()
    )

    # Keep only hostnames associated with one class.
    single_class_hostnames = hostname_class_counts[
        hostname_class_counts == 1
    ].index

    domain_df = df[
        df["hostname"].isin(single_class_hostnames)
    ].copy()

    hostname_labels = (
        domain_df.groupby("hostname")["type"]
        .first()
        .reset_index()
    )

    train_hosts, test_hosts = train_test_split(
        hostname_labels,
        test_size=0.20,
        random_state=42,
        stratify=hostname_labels["type"],
    )

    train_host_set = set(train_hosts["hostname"])
    test_host_set = set(test_hosts["hostname"])

    shared_hosts = train_host_set & test_host_set

    if shared_hosts:
        raise ValueError(
            "Domain leakage detected."
        )

    train_df = domain_df[
        domain_df["hostname"].isin(train_host_set)
    ]

    test_df = domain_df[
        domain_df["hostname"].isin(test_host_set)
    ]

    X_train = train_df[FEATURE_NAMES]
    X_test = test_df[FEATURE_NAMES]

    y_train = train_df["type"]
    y_test = test_df["type"]

    print(f"Training rows: {len(train_df):,}")
    print(f"Testing rows:  {len(test_df):,}")
    print(f"Training domains: {len(train_host_set):,}")
    print(f"Testing domains:  {len(test_host_set):,}")
    print(f"Shared domains: {len(shared_hosts)}")

    # Train ONLY on training domains.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    print("\nTraining evaluation model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    confidence = probabilities.max(axis=1)

    errors = predictions != y_test.to_numpy()

    print("\n" + "=" * 70)
    print("Final Unseen-Domain Results")
    print("=" * 70)

    print(
        f"\nAccuracy: "
        f"{accuracy_score(y_test, predictions):.4f}"
    )

    print(
        "Macro Precision: "
        f"{precision_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        "Macro Recall: "
        f"{recall_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        "Macro F1: "
        f"{f1_score(y_test, predictions, average='macro'):.4f}"
    )

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
        )
    )

    print("Confusion Matrix:")

    matrix = pd.DataFrame(
        confusion_matrix(
            y_test,
            predictions,
        ),
        index=model.classes_,
        columns=model.classes_,
    )

    print(matrix.to_string())

    print("\nError Analysis:")
    print(f"Total errors: {errors.sum():,}")

    for threshold in [0.50, 0.70, 0.90, 0.95, 0.99]:
        high_confidence_errors = (
            errors
            & (confidence >= threshold)
        ).sum()

        print(
            f"Confidence >= {threshold:.2f}: "
            f"{high_confidence_errors:,} high-confidence errors"
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
