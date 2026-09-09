from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "cleaned_urls.csv"
)


def extract_hostname(url: str) -> str:
    """Extract hostname from a URL."""

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
    """Analyze URL-level and domain-aware train/test splits."""

    df = pd.read_csv(DATASET_PATH)

    df["hostname"] = df["url"].apply(extract_hostname)

    print("=" * 70)
    print("WebLens Train/Test Split Analysis")
    print("=" * 70)

    print(f"\nTotal rows: {len(df):,}")
    print(f"Unique URLs: {df['url'].nunique():,}")
    print(f"Unique hostnames: {df['hostname'].nunique():,}")

    # ---------------------------------------------------------
    # Split A: Random stratified URL-level split
    # ---------------------------------------------------------

    train_random, test_random = train_test_split(
        df,
        test_size=0.20,
        random_state=42,
        stratify=df["type"],
    )

    print("\n" + "-" * 70)
    print("Split A: Random Stratified URL Split")
    print("-" * 70)

    print(f"Training rows: {len(train_random):,}")
    print(f"Testing rows:  {len(test_random):,}")

    print("\nTraining class distribution:")

    print(
        train_random["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    print("\nTesting class distribution:")

    print(
        test_random["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    shared_urls = set(train_random["url"]) & set(test_random["url"])

    shared_hostnames = (
        set(train_random["hostname"])
        & set(test_random["hostname"])
    )

    print(f"\nURLs shared between train/test: {len(shared_urls):,}")
    print(
        "Hostnames shared between train/test: "
        f"{len(shared_hostnames):,}"
    )

    # ---------------------------------------------------------
    # Split B: Domain-aware split
    # ---------------------------------------------------------

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

    print("\n" + "-" * 70)
    print("Domain Structure")
    print("-" * 70)

    print(
        "Single-class hostnames: "
        f"{len(single_class_hostnames):,}"
    )

    print(
        "Multi-class hostnames: "
        f"{len(multi_class_hostnames):,}"
    )

    # We only use single-class hostnames for a strict domain split.
    # This avoids putting a hostname with different labels into
    # both training and testing sets.
    single_class_df = df[
        df["hostname"].isin(single_class_hostnames)
    ].copy()

    print(
        "\nRows belonging to single-class hostnames: "
        f"{len(single_class_df):,}"
    )

    print(
        "Rows excluded from strict domain split: "
        f"{len(df) - len(single_class_df):,}"
    )

    # Split hostnames rather than individual URLs.
    hostname_labels = (
        single_class_df.groupby("hostname")["type"]
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

    train_domain = single_class_df[
        single_class_df["hostname"].isin(train_host_set)
    ]

    test_domain = single_class_df[
        single_class_df["hostname"].isin(test_host_set)
    ]

    print("\n" + "-" * 70)
    print("Split B: Strict Domain-Aware Split")
    print("-" * 70)

    print(f"Training rows: {len(train_domain):,}")
    print(f"Testing rows:  {len(test_domain):,}")

    print("\nTraining class distribution:")

    print(
        train_domain["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    print("\nTesting class distribution:")

    print(
        test_domain["type"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    shared_domain_hosts = (
        set(train_domain["hostname"])
        & set(test_domain["hostname"])
    )

    print(
        "\nHostnames shared between domain train/test: "
        f"{len(shared_domain_hosts):,}"
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
