from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "malicious_phish.csv"


def extract_hostname(url: str) -> str:
    """Extract hostname from a URL, including URLs without a scheme."""

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
    """Analyze domain distribution and cross-class domains."""

    df = pd.read_csv(DATASET_PATH)

    df["url"] = df["url"].str.strip()

    df["hostname"] = df["url"].apply(extract_hostname)

    print("=" * 70)
    print("WebLens Domain Analysis")
    print("=" * 70)

    print("\nURLs with extracted hostname:")
    print((df["hostname"] != "").sum())

    print("\nURLs without extracted hostname:")
    print((df["hostname"] == "").sum())

    print("\nUnique hostnames:")
    print(df["hostname"].nunique())

    hostname_counts = df["hostname"].value_counts()

    print("\nTop 20 hostnames by URL count:")
    print(hostname_counts.head(20).to_string())

    print("\nHostnames appearing more than once:")
    print((hostname_counts > 1).sum())

    print("\nHostnames appearing in multiple classes:")

    class_counts = df.groupby("hostname")["type"].nunique()

    multi_class_hostnames = class_counts[
        (class_counts > 1) & (df.groupby("hostname").size() > 1)
    ]

    print(len(multi_class_hostnames))

    if len(multi_class_hostnames) > 0:
        print("\nExample multi-class hostnames:")

        examples = (
            df[df["hostname"].isin(multi_class_hostnames.index)]
            .groupby(["hostname", "type"])
            .size()
            .sort_values(ascending=False)
            .head(30)
        )

        print(examples.to_string())

    print("\nURLs per hostname statistics:")

    print(
        hostname_counts.describe(
            percentiles=[0.5, 0.75, 0.90, 0.95, 0.99]
        ).round(2).to_string()
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
