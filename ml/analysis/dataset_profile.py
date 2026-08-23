from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "malicious_phish.csv"


def main() -> None:
    """Generate a basic profile of the WebLens malicious URL dataset."""

    df = pd.read_csv(DATASET_PATH)

    df["url_normalized"] = df["url"].str.strip()

    duplicate_rows = df.duplicated().sum()
    duplicate_urls = df["url"].duplicated().sum()

    label_counts = df.groupby("url")["type"].nunique()
    conflicting_urls = label_counts[label_counts > 1]

    print("=" * 60)
    print("WebLens Dataset Profile")
    print("=" * 60)

    print(f"\nDataset: {DATASET_PATH}")
    print(f"Rows: {len(df):,}")
    print("Original columns: 2")

    print("\nColumns:")
    print(df[["url", "type"]].columns.tolist())

    print("\nClass distribution:")
    print(df["type"].value_counts().to_string())

    print("\nClass percentages:")
    percentages = df["type"].value_counts(normalize=True).mul(100)
    print(percentages.round(2).to_string())

    print("\nMissing values:")
    print(df[["url", "type"]].isnull().sum().to_string())

    print("\nEmpty URLs:")
    print((df["url"].str.strip() == "").sum())

    print("\nWhitespace anomalies:")
    print((df["url"] != df["url_normalized"]).sum())

    print("\nDuplicate rows:")
    print(duplicate_rows)

    print("\nDuplicate URLs:")
    print(duplicate_urls)

    print("\nUnique URLs:")
    print(df["url"].nunique())

    print("\nURLs appearing more than once:")
    url_counts = df.groupby("url").size()
    print((url_counts > 1).sum())

    print("\nURLs with conflicting labels:")
    print(len(conflicting_urls))

    if len(conflicting_urls) > 0:
        print("\nConflicting URLs:")
        print(
            df[df["url"].isin(conflicting_urls.index)][["url", "type"]]
            .sort_values("url")
            .to_string(index=False)
        )

    print("\nNormalized URL statistics:")
    print(f"Normalized unique URLs: {df['url_normalized'].nunique():,}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
