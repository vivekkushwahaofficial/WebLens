from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "raw"
    / "malicious_phish.csv"
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
    """Measure domain concentration within each class."""

    df = pd.read_csv(DATASET_PATH)

    df["url"] = df["url"].str.strip()
    df["hostname"] = df["url"].apply(extract_hostname)

    print("=" * 70)
    print("WebLens Domain Class Concentration Analysis")
    print("=" * 70)

    for label in sorted(df["type"].unique()):

        class_df = df[df["type"] == label]

        domain_counts = class_df["hostname"].value_counts()

        print(f"\nClass: {label}")
        print("-" * 70)

        print(f"URLs: {len(class_df):,}")
        print(f"Unique hostnames: {domain_counts.size:,}")

        print("\nTop 10 hostnames:")

        top10 = domain_counts.head(10)

        result = pd.DataFrame(
            {
                "count": top10,
                "percentage": (
                    top10 / len(class_df) * 100
                ).round(3),
            }
        )

        print(result.to_string())

        print("\nTop 10 concentration:")

        top10_percentage = (
            domain_counts.head(10).sum()
            / len(class_df)
            * 100
        )

        print(f"{top10_percentage:.3f}%")

        print("\nTop 100 concentration:")

        top100_percentage = (
            domain_counts.head(100).sum()
            / len(class_df)
            * 100
        )

        print(f"{top100_percentage:.3f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
