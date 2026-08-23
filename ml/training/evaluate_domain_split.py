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

from ml.features.url_features import FEATURE_NAMES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_features.csv"
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


def evaluate_model(model, x_train, x_test, y_train, y_test):
    """Train and evaluate the domain-aware baseline."""

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    print("\n" + "=" * 70)
    print("Domain-Aware Random Forest Results")
    print("=" * 70)

    print(f"\nAccuracy: {accuracy_score(y_test, predictions):.4f}")

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


def main() -> None:
    """Evaluate URL features using unseen hostnames."""

    print("=" * 70)
    print("WebLens Domain-Aware Baseline Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nTotal rows: {len(df):,}")

    # Validate the feature schema.
    missing_features = [
        name for name in FEATURE_NAMES
        if name not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Extract hostname for domain-level splitting.
    df["hostname"] = df["url"].apply(extract_hostname)

    print(f"Unique hostnames: {df['hostname'].nunique():,}")

    # Count distinct labels associated with each hostname.
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

    # Strict evaluation dataset.
    #
    # Multi-class hostnames are excluded because assigning their
    # hostname to only one side could create label leakage.
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

    # Create one label per hostname.
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
            "Domain leakage detected: train and test share hostnames"
        )

    train_df = domain_df[
        domain_df["hostname"].isin(train_host_set)
    ].copy()

    test_df = domain_df[
        domain_df["hostname"].isin(test_host_set)
    ].copy()

    print("\nTraining rows:", f"{len(train_df):,}")
    print("Testing rows: ", f"{len(test_df):,}")

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

    # Select only the canonical ML features.
    x_train = train_df[FEATURE_NAMES]
    x_test = test_df[FEATURE_NAMES]

    y_train = train_df["type"]
    y_test = test_df["type"]

    # Same baseline configuration used in the random URL split.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    evaluate_model(
        model,
        x_train,
        x_test,
        y_train,
        y_test,
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
