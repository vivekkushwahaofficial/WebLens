from pathlib import Path

import pandas as pd

from ml.features.url_features import FEATURE_NAMES
from ml.features.url_features import extract_url_features
from ml.features.url_features import features_to_vector


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "cleaned_urls.csv"
)

OUTPUT_DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_features.csv"
)


def main() -> None:
    """Generate the ML feature dataset from cleaned URLs."""

    print("=" * 70)
    print("WebLens Feature Generation")
    print("=" * 70)

    # Load the cleaned dataset.
    df = pd.read_csv(INPUT_DATASET_PATH)

    print(f"\nInput rows: {len(df):,}")

    # Validate required columns.
    required_columns = {"url", "type"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: "
            f"{required_columns - set(df.columns)}"
        )

    # Extract feature dictionaries from every URL.
    feature_dicts = df["url"].apply(extract_url_features)

    # Convert feature dictionaries into the canonical feature order.
    feature_vectors = feature_dicts.apply(features_to_vector)

    # Build the feature DataFrame.
    feature_df = pd.DataFrame(
        feature_vectors.tolist(),
        columns=FEATURE_NAMES,
    )

    # Keep URL and label for traceability.
    result_df = pd.concat(
        [
            df[["url", "type"]].reset_index(drop=True),
            feature_df.reset_index(drop=True),
        ],
        axis=1,
    )

    # Validate feature count.
    if len(FEATURE_NAMES) != 27:
        raise ValueError(
            f"Expected 27 features, found {len(FEATURE_NAMES)}"
        )

    if feature_df.shape[1] != 27:
        raise ValueError(
            f"Generated {feature_df.shape[1]} features instead of 27"
        )

    # Validate missing values.
    missing_values = result_df[
        FEATURE_NAMES
    ].isnull().sum().sum()

    if missing_values != 0:
        raise ValueError(
            f"Feature dataset contains {missing_values} missing values"
        )

    # Validate that every feature is numeric.
    non_numeric_columns = feature_df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if non_numeric_columns:
        raise ValueError(
            f"Non-numeric features found: {non_numeric_columns}"
        )

    # Validate labels were preserved.
    if len(result_df) != len(df):
        raise ValueError("Row count changed during feature generation")

    # Create output directory.
    OUTPUT_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the generated feature dataset.
    result_df.to_csv(
        OUTPUT_DATASET_PATH,
        index=False,
    )

    print(f"Generated features: {len(FEATURE_NAMES)}")
    print(f"Output rows: {len(result_df):,}")

    print("\nFeature columns:")
    print(FEATURE_NAMES)

    print("\nMissing feature values:")
    print(
        result_df[FEATURE_NAMES]
        .isnull()
        .sum()
        .sum()
    )

    print("\nNon-numeric feature columns:")
    print(non_numeric_columns)

    print("\nClass distribution:")
    print(
        result_df["type"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(f"\nOutput: {OUTPUT_DATASET_PATH}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
