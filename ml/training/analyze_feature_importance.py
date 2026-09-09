from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
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
    """Analyze Random Forest feature importance on unseen domains."""

    print("=" * 70)
    print("WebLens Feature Importance Analysis")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nTotal rows: {len(df):,}")
    print(f"Total features: {len(FEATURE_NAMES)}")

    if len(FEATURE_NAMES) != 46:
        raise ValueError(
            f"Expected 46 features, found {len(FEATURE_NAMES)}"
        )

    missing_features = [
        feature
        for feature in FEATURE_NAMES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

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

    X_train = train_df[FEATURE_NAMES]
    X_test = test_df[FEATURE_NAMES]

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

    importance_df = pd.DataFrame(
        {
            "feature": FEATURE_NAMES,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    importance_df["percentage"] = (
        importance_df["importance"] * 100
    ).round(3)

    print("\nTop 20 Features:")
    print("-" * 70)

    print(
        importance_df.head(20)[
            ["feature", "percentage"]
        ].to_string(index=False)
    )

    print("\nAll Features:")
    print("-" * 70)

    print(
        importance_df[
            ["feature", "percentage"]
        ].to_string(index=False)
    )

    print("\nFeature importance total:")
    print(
        f"{importance_df['importance'].sum():.6f}"
    )

    print("\nTrain/Test:")
    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows:  {len(X_test):,}")
    print(f"Shared domains: {len(train_host_set & test_host_set)}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
