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


def extract_hostname(url: str) -> str:
    """Extract a normalized hostname from a URL."""

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
    """Evaluate the 46-feature Random Forest on unseen hostnames."""

    print("=" * 70)
    print("WebLens Enhanced Domain-Aware Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nTotal rows: {len(df):,}")
    print(f"Feature count: {len(FEATURE_NAMES)}")

    if len(FEATURE_NAMES) != 46:
        raise ValueError(
            f"Expected 46 features, found {len(FEATURE_NAMES)}"
        )

    missing_features = [
        name for name in FEATURE_NAMES
        if name not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Extract hostname for strict domain-aware splitting.
    df["hostname"] = df["url"].apply(extract_hostname)

    print(f"Unique hostnames: {df['hostname'].nunique():,}")

    # Determine whether each hostname belongs to one or multiple classes.
    hostname_class_counts = (
        df.groupby("hostname")["type"]
        .nunique()
    )

    single_class_hostnames = hostname_class_counts[
        hostname_class_counts == 1
    ].index

    multi_class_hostnames = hostname_class_counts[
        hostname_class_counts > 1
    ].index

    print(
        "Single-class hostnames: "
        f"{len(single_class_hostnames):,}"
    )

    print(
        "Multi-class hostnames: "
        f"{len(multi_class_hostnames):,}"
    )

    # Exclude multi-class hostnames for strict evaluation.
    domain_df = df[
        df["hostname"].isin(single_class_hostnames)
    ].copy()

    print(
        "\nRows used for strict domain evaluation: "
        f"{len(domain_df):,}"
    )

    print(
        "Rows excluded: "
        f"{len(df) - len(domain_df):,}"
    )

    # Create one label for every hostname.
    hostname_labels = (
        domain_df.groupby("hostname")["type"]
        .first()
        .reset_index()
    )

    # Split hostnames, not individual URLs.
    train_hosts, test_hosts = train_test_split(
        hostname_labels,
        test_size=0.20,
        random_state=42,
        stratify=hostname_labels["type"],
    )

    train_host_set = set(train_hosts["hostname"])
    test_host_set = set(test_hosts["hostname"])

    # Explicit leakage check.
    shared_hostnames = train_host_set & test_host_set

    print(
        "\nShared train/test hostnames: "
        f"{len(shared_hostnames):,}"
    )

    if shared_hostnames:
        raise ValueError(
            "Domain leakage detected."
        )

    train_df = domain_df[
        domain_df["hostname"].isin(train_host_set)
    ].copy()

    test_df = domain_df[
        domain_df["hostname"].isin(test_host_set)
    ].copy()

    print(f"\nTraining rows: {len(train_df):,}")
    print(f"Testing rows:  {len(test_df):,}")

    print("\nTraining class distribution:")
    print(
        train_df["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    print("\nTesting class distribution:")
    print(
        test_df["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    # Select exactly the canonical 46 features.
    x_train = train_df[FEATURE_NAMES]
    x_test = test_df[FEATURE_NAMES]

    y_train = train_df["type"]
    y_test = test_df["type"]

    # Validate feature values.
    if x_train.isnull().sum().sum() != 0:
        raise ValueError("Training features contain missing values.")

    if x_test.isnull().sum().sum() != 0:
        raise ValueError("Testing features contain missing values.")

    # Same Random Forest configuration as the 27-feature baseline.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    print("\nTraining Random Forest...")
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    print("\n" + "=" * 70)
    print("46-Feature Domain-Aware Random Forest Results")
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
    print(confusion_matrix(y_test, predictions))

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
