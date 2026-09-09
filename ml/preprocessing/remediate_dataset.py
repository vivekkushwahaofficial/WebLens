from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASE_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "cleaned_urls.csv"
)

CURATED_BENIGN_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "curated"
    / "benign_urls.csv"
)

OUTPUT_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "remediated_urls.csv"
)

EXPECTED_LABELS = {
    "benign",
    "defacement",
    "phishing",
    "malware",
}


def normalize_url(value: object) -> str:
    """Normalize a URL for duplicate detection."""

    return str(value).strip().strip("'").strip('"')


def main() -> None:
    """Build the remediated WebLens training dataset."""

    print("=" * 70)
    print("WebLens Dataset Remediation")
    print("=" * 70)

    # Load the existing cleaned dataset.
    base_df = pd.read_csv(BASE_DATASET_PATH)

    # Load the curated legitimate URL corpus.
    curated_df = pd.read_csv(CURATED_BENIGN_PATH)

    required_columns = {"url", "type"}

    if not required_columns.issubset(base_df.columns):
        raise ValueError(
            "Base dataset must contain 'url' and 'type'."
        )

    if not required_columns.issubset(curated_df.columns):
        raise ValueError(
            "Curated dataset must contain 'url' and 'type'."
        )

    # Normalize URLs.
    base_df["url"] = base_df["url"].map(normalize_url)
    curated_df["url"] = curated_df["url"].map(normalize_url)

    # Validate curated labels.
    curated_labels = set(
        curated_df["type"].dropna().unique()
    )

    if curated_labels != {"benign"}:
        raise ValueError(
            "Curated benign dataset may contain only "
            "the 'benign' label."
        )

    # Remove invalid curated rows.
    curated_df = curated_df.dropna(
        subset=["url", "type"]
    ).copy()

    curated_df = curated_df[
        curated_df["url"] != ""
    ].copy()

    # Remove duplicates inside curated data.
    curated_before = len(curated_df)

    curated_df = curated_df.drop_duplicates(
        subset=["url"],
        keep="first",
    ).copy()

    print(
        f"\nCurated rows: {curated_before:,}"
    )

    print(
        f"Curated duplicate URLs removed: "
        f"{curated_before - len(curated_df):,}"
    )

    # Do not add URLs already present in the base dataset.
    existing_urls = set(base_df["url"])

    new_curated_df = curated_df[
        ~curated_df["url"].isin(existing_urls)
    ].copy()

    print(
        f"New curated URLs added: "
        f"{len(new_curated_df):,}"
    )

    # Combine original data with curated legitimate URLs.
    result_df = pd.concat(
        [
            base_df[["url", "type"]],
            new_curated_df[["url", "type"]],
        ],
        ignore_index=True,
    )

    # Remove exact duplicate URL + label rows.
    result_df = result_df.drop_duplicates(
        subset=["url", "type"],
        keep="first",
    ).copy()

    # Detect conflicting labels.
    label_counts = (
        result_df.groupby("url")["type"]
        .nunique()
    )

    conflicting_urls = set(
        label_counts[label_counts > 1].index
    )

    if conflicting_urls:
        raise ValueError(
            f"Found {len(conflicting_urls):,} URLs "
            "with conflicting labels after remediation."
        )

    # Deterministic ordering.
    result_df = result_df.sort_values(
        ["type", "url"],
        kind="stable",
    ).reset_index(drop=True)

    # Validate final labels.
    labels = set(
        result_df["type"].dropna().unique()
    )

    unexpected_labels = labels - EXPECTED_LABELS

    if unexpected_labels:
        raise ValueError(
            f"Unexpected labels: {unexpected_labels}"
        )

    # Save the remediated dataset.
    OUTPUT_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        OUTPUT_DATASET_PATH,
        index=False,
    )

    print(
        f"\nOriginal rows: "
        f"{len(base_df):,}"
    )

    print(
        f"Final rows: "
        f"{len(result_df):,}"
    )

    print("\nFinal class distribution:")

    print(
        result_df["type"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nFinal class percentages:")

    print(
        (
            result_df["type"]
            .value_counts(normalize=True)
            .sort_index()
            .mul(100)
            .round(2)
        ).to_string()
    )

    print(
        "\nConflicting URLs: "
        f"{len(conflicting_urls):,}"
    )

    print(
        f"\nOutput: "
        f"{OUTPUT_DATASET_PATH}"
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
