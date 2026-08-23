from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "raw"
    / "malicious_phish.csv"
)

PROCESSED_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "cleaned_urls.csv"
)

EXPECTED_LABELS = {
    "benign",
    "defacement",
    "phishing",
    "malware",
}


def main() -> None:
    """Clean the raw WebLens URL dataset."""

    print("=" * 70)
    print("WebLens Dataset Cleaning")
    print("=" * 70)

    # Load the original dataset.
    df = pd.read_csv(RAW_DATASET_PATH)

    print(f"\nRaw rows: {len(df):,}")

    # Normalize leading and trailing whitespace.
    df["url"] = df["url"].str.strip()

    # Validate required columns.
    required_columns = {"url", "type"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: "
            f"{required_columns - set(df.columns)}"
        )

    # Validate labels before modifying the dataset.
    labels = set(df["type"].dropna().unique())

    unexpected_labels = labels - EXPECTED_LABELS

    if unexpected_labels:
        raise ValueError(
            f"Unexpected labels found: {unexpected_labels}"
        )

    # Remove rows with missing URL or label.
    before_missing_removal = len(df)

    df = df.dropna(subset=["url", "type"]).copy()

    print(
        "Rows removed because of missing values: "
        f"{before_missing_removal - len(df):,}"
    )

    # Remove empty URLs.
    before_empty_removal = len(df)

    df = df[df["url"] != ""].copy()

    print(
        "Rows removed because of empty URLs: "
        f"{before_empty_removal - len(df):,}"
    )

    # Remove exact duplicate URL + label rows.
    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["url", "type"],
        keep="first",
    ).copy()

    print(
        "Exact duplicate rows removed: "
        f"{before_duplicates - len(df):,}"
    )

    # Find URLs that have conflicting labels.
    label_counts = df.groupby("url")["type"].nunique()

    conflicting_urls = set(
        label_counts[label_counts > 1].index
    )

    print(
        "Conflicting URL groups detected: "
        f"{len(conflicting_urls):,}"
    )

    # Remove all rows belonging to conflicting URL groups.
    before_conflict_removal = len(df)

    if conflicting_urls:
        df = df[
            ~df["url"].isin(conflicting_urls)
        ].copy()

    print(
        "Rows removed because of conflicting labels: "
        f"{before_conflict_removal - len(df):,}"
    )

    # Sort for deterministic output.
    df = df.sort_values(
        ["type", "url"],
        kind="stable",
    ).reset_index(drop=True)

    # Create the processed-data directory.
    PROCESSED_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the cleaned dataset.
    df.to_csv(
        PROCESSED_DATASET_PATH,
        index=False,
    )

    print(f"\nFinal rows: {len(df):,}")

    print("\nFinal class distribution:")

    print(
        df["type"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nFinal class percentages:")

    print(
        (
            df["type"]
            .value_counts(normalize=True)
            .sort_index()
            .mul(100)
            .round(2)
        ).to_string()
    )

    print("\nFinal validation:")

    print(
        f"Missing values: "
        f"{df[['url', 'type']].isnull().sum().sum()}"
    )

    print(
        f"Duplicate URL + label rows: "
        f"{df.duplicated(subset=['url', 'type']).sum()}"
    )

    remaining_conflicts = (
        df.groupby("url")["type"].nunique()
    )

    print(
        "Conflicting URL groups remaining: "
        f"{(remaining_conflicts > 1).sum()}"
    )

    print(
        f"\nOutput: {PROCESSED_DATASET_PATH}"
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
