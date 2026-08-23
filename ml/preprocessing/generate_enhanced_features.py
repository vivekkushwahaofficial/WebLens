from pathlib import Path

import pandas as pd

from ml.features.url_component_features import (
    extract_url_component_features,
)
from ml.features.url_features import (
    FEATURE_NAMES as BASE_FEATURE_NAMES,
)
from ml.features.url_features import (
    extract_url_features,
)
from ml.features.url_features import (
    features_to_vector,
)


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
    / "url_enhanced_features.csv"
)


COMPONENT_FEATURE_NAMES = [
    "hostname_length",
    "hostname_digit_count",
    "hostname_hyphen_count",
    "hostname_dot_count",
    "subdomain_count",
    "path_length",
    "path_digit_count",
    "path_special_char_count",
    "path_depth",
    "query_length",
    "query_parameter_count",
    "query_digit_count",
    "query_special_char_count",
    "hostname_entropy",
    "path_entropy",
    "query_entropy",
    "has_query",
    "has_fragment",
    "has_port",
]


FEATURE_NAMES = BASE_FEATURE_NAMES + COMPONENT_FEATURE_NAMES


def main() -> None:
    """Generate the enhanced 45-feature URL dataset."""

    print("=" * 70)
    print("WebLens Enhanced Feature Generation")
    print("=" * 70)

    df = pd.read_csv(INPUT_DATASET_PATH)

    print(f"\nInput rows: {len(df):,}")

    required_columns = {"url", "type"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: "
            f"{required_columns - set(df.columns)}"
        )

    # Generate the original 27 lexical features.
    base_feature_dicts = df["url"].apply(
        extract_url_features
    )

    base_vectors = base_feature_dicts.apply(
        features_to_vector
    )

    base_df = pd.DataFrame(
        base_vectors.tolist(),
        columns=BASE_FEATURE_NAMES,
    )

    # Generate the 18 URL component features.
    component_feature_dicts = df["url"].apply(
        extract_url_component_features
    )

    component_df = pd.DataFrame(
        component_feature_dicts.tolist(),
        columns=COMPONENT_FEATURE_NAMES,
    )

    # Combine both feature groups.
    feature_df = pd.concat(
        [
            base_df.reset_index(drop=True),
            component_df.reset_index(drop=True),
        ],
        axis=1,
    )

    if len(FEATURE_NAMES) != 46:
        raise ValueError(
            f"Expected 46 features, found {len(FEATURE_NAMES)}"
        )

    if feature_df.shape[1] != 46:
        raise ValueError(
            f"Generated {feature_df.shape[1]} features "
            "instead of 46"
        )

    # Validate feature names and ordering.
    if feature_df.columns.tolist() != FEATURE_NAMES:
        raise ValueError(
            "Feature column order does not match "
            "the canonical enhanced schema"
        )

    # Validate missing values.
    missing_values = (
        feature_df.isnull().sum().sum()
    )

    if missing_values:
        raise ValueError(
            f"Found {missing_values} missing feature values"
        )

    # Validate numeric values.
    non_numeric_columns = feature_df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if non_numeric_columns:
        raise ValueError(
            f"Non-numeric features found: "
            f"{non_numeric_columns}"
        )

    # Preserve URL and label for traceability.
    result_df = pd.concat(
        [
            df[["url", "type"]].reset_index(drop=True),
            feature_df.reset_index(drop=True),
        ],
        axis=1,
    )

    if len(result_df) != len(df):
        raise ValueError(
            "Row count changed during feature generation"
        )

    OUTPUT_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        OUTPUT_DATASET_PATH,
        index=False,
    )

    print(f"Base features: {len(BASE_FEATURE_NAMES)}")
    print(
        f"Component features: "
        f"{len(COMPONENT_FEATURE_NAMES)}"
    )
    print(f"Total features: {len(FEATURE_NAMES)}")
    print(f"Output rows: {len(result_df):,}")

    print("\nMissing values:")
    print(missing_values)

    print("\nNon-numeric columns:")
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
