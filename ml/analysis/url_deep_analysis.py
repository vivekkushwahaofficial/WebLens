from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "malicious_phish.csv"


SUSPICIOUS_TERMS = [
    "login",
    "signin",
    "verify",
    "account",
    "update",
    "secure",
    "bank",
    "password",
    "confirm",
]


def main() -> None:
    """Analyze URL distributions and keyword patterns."""

    df = pd.read_csv(DATASET_PATH)

    df["url"] = df["url"].str.strip()

    df["url_length"] = df["url"].str.len()

    print("=" * 70)
    print("WebLens Deep URL Analysis")
    print("=" * 70)

    print("\nURL length percentiles by class:")

    percentiles = (
        df.groupby("type")["url_length"]
        .quantile([0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
        .unstack()
    )

    percentiles.columns = [
        "P25",
        "P50",
        "P75",
        "P90",
        "P95",
        "P99",
    ]

    print(percentiles.round(2).to_string())

    print("\nSuspicious keyword occurrence by class:")

    keyword_results = {}

    for term in SUSPICIOUS_TERMS:
        contains_term = df["url"].str.contains(
            term,
            case=False,
            regex=False,
            na=False,
        )

        rates = (
            df.assign(contains_term=contains_term)
            .groupby("type")["contains_term"]
            .mean()
            .mul(100)
        )

        keyword_results[term] = rates

    keyword_df = pd.DataFrame(keyword_results).T

    print(keyword_df.round(3).to_string())

    print("\nKeyword occurrence counts:")

    for term in SUSPICIOUS_TERMS:
        contains_term = df["url"].str.contains(
            term,
            case=False,
            regex=False,
            na=False,
        )

        print(f"\n{term}:")
        print(df[contains_term]["type"].value_counts().to_string())

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
