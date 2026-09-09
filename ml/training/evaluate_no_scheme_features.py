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

FEATURE_NAMES = (
    BASE_FEATURE_NAMES
    + COMPONENT_FEATURE_NAMES
)

# Remove features strongly tied to dataset collection/protocol.
EXCLUDED_FEATURES = {
    "has_http",
    "has_https",
}

MODEL_FEATURE_NAMES = [
    feature
    for feature in FEATURE_NAMES
    if feature not in EXCLUDED_FEATURES
]


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
    """Evaluate the model without scheme-dependent features."""

    print("=" * 70)
    print("WebLens No-Scheme-Feature Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nTotal rows: {len(df):,}")
    print(f"Original features: {len(FEATURE_NAMES)}")
    print(f"Experiment features: {len(MODEL_FEATURE_NAMES)}")

    df["hostname"] = df["url"].apply(extract_hostname)

    hostname_class_counts = (
        df.groupby("hostname")["type"]
        .nunique()
    )

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

    if train_host_set & test_host_set:
        raise ValueError(
            "Domain leakage detected."
        )

    train_df = domain_df[
        domain_df["hostname"].isin(train_host_set)
    ]

    test_df = domain_df[
        domain_df["hostname"].isin(test_host_set)
    ]

    X_train = train_df[MODEL_FEATURE_NAMES]
    X_test = test_df[MODEL_FEATURE_NAMES]

    y_train = train_df["type"]
    y_test = test_df["type"]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    print("\nTraining Random Forest...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n" + "=" * 70)
    print("No-Scheme-Feature Results")
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
    print(classification_report(y_test, predictions))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nExcluded features:")
    print(sorted(EXCLUDED_FEATURES))

    print("\nTraining rows:", f"{len(X_train):,}")
    print("Testing rows: ", f"{len(X_test):,}")
    print(
        "Shared hostnames:",
        len(train_host_set & test_host_set),
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
