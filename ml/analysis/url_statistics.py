from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "malicious_phish.csv"


def main() -> None:
    """Analyze basic URL characteristics by malicious URL class."""

    df = pd.read_csv(DATASET_PATH)

    # Normalize whitespace for analysis.
    df["url"] = df["url"].str.strip()

    # Basic URL-level features.
    df["url_length"] = df["url"].str.len()

    df["digit_count"] = df["url"].str.count(r"\d")

    df["letter_count"] = df["url"].str.count(r"[A-Za-z]")

    df["special_char_count"] = df["url"].str.count(r"[^A-Za-z0-9]")

    df["dot_count"] = df["url"].str.count(r"\.")

    df["hyphen_count"] = df["url"].str.count("-")

    df["slash_count"] = df["url"].str.count("/")

    df["question_count"] = df["url"].str.count(r"\?")

    df["equals_count"] = df["url"].str.count("=")

    df["ampersand_count"] = df["url"].str.count("&")

    df["at_count"] = df["url"].str.count("@")

    df["percent_count"] = df["url"].str.count("%")

    df["underscore_count"] = df["url"].str.count("_")

    # Suspicious URL indicators.
    df["has_ip_address"] = df["url"].str.match(
        r"^(?:https?://)?(?:\d{1,3}\.){3}\d{1,3}",
        case=False,
        na=False,
    )

    df["has_https"] = df["url"].str.startswith(
        "https://",
        na=False,
    )

    df["has_http"] = df["url"].str.startswith(
        "http://",
        na=False,
    )

    df["has_at_symbol"] = df["url"].str.contains(
        "@",
        regex=False,
        na=False,
    )

    df["has_percent_encoding"] = df["url"].str.contains(
        "%",
        regex=False,
        na=False,
    )

    feature_columns = [
        "url_length",
        "digit_count",
        "letter_count",
        "special_char_count",
        "dot_count",
        "hyphen_count",
        "slash_count",
        "question_count",
        "equals_count",
        "ampersand_count",
        "at_count",
        "percent_count",
        "underscore_count",
    ]

    print("=" * 70)
    print("WebLens URL Statistical Analysis")
    print("=" * 70)

    print("\nFeature statistics by class:")

    statistics = df.groupby("type")[feature_columns].agg(
        ["mean", "median", "max"]
    )

    print(statistics.round(2).to_string())

    print("\nBinary indicator rates by class:")

    indicator_columns = [
        "has_ip_address",
        "has_https",
        "has_http",
        "has_at_symbol",
        "has_percent_encoding",
    ]

    indicator_rates = df.groupby("type")[indicator_columns].mean() * 100

    print(indicator_rates.round(2).to_string())

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
