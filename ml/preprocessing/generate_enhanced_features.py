from pathlib import Path
import argparse

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

PROCESSED_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
)

DATASET_PATHS = {
    "cleaned": PROCESSED_DIR / "cleaned_urls.csv",
    "remediated": PROCESSED_DIR / "remediated_urls.csv",
}

OUTPUT_PATHS = {
    "cleaned": PROCESSED_DIR / "url_enhanced_features.csv",
    "remediated": (
        PROCESSED_DIR
        / "url_enhanced_features_remediated.csv"
    ),
}


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


EXTENSION_FEATURE_NAMES = [
    "has_exe_extension",
    "has_html_extension",
    "has_bin_extension",
    "has_asp_extension",
]


EXCLUDED_BASE_FEATURES = {
    "has_http",
    "has_https",
}


FEATURE_NAMES = [
    feature
    for feature in BASE_FEATURE_NAMES
    if feature not in EXCLUDED_BASE_FEATURES
] + COMPONENT_FEATURE_NAMES + EXTENSION_FEATURE_NAMES


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate WebLens enhanced URL features."
        )
    )

    parser.add_argument(
        "--input",
        choices=DATASET_PATHS.keys(),
        default="cleaned",
        help=(
            "Dataset to process: "
            "'cleaned' or 'remediated'. "
            "Default: cleaned."
        ),
    )

    return parser.parse_args()


def main() -> None:
    """Generate the enhanced 48-feature URL dataset."""

    args = parse_arguments()

    input_path = DATASET_PATHS[args.input]
    output_path = OUTPUT_PATHS[args.input]

    print("=" * 70)
    print("WebLens Enhanced Feature Generation")
    print("=" * 70)

    print(f"\nInput mode: {args.input}")
    print(f"Input path: {input_path}")

    df = pd.read_csv(input_path)

    print(f"\nInput rows: {len(df):,}")

    required_columns = {"url", "type"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: "
            f"{required_columns - set(df.columns)}"
        )

    # Generate the base lexical features.
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

    # Remove protocol-dependent features.
    base_df = base_df.drop(
        columns=list(EXCLUDED_BASE_FEATURES)
    )

    # Generate URL component features.
    component_feature_dicts = df["url"].apply(
        extract_url_component_features
    )

    component_df = pd.DataFrame(
        component_feature_dicts.tolist(),
        columns=COMPONENT_FEATURE_NAMES,
    )

    # Generate extension features.
    url_lower = df["url"].astype(str).str.lower()

    extension_df = pd.DataFrame(
        {
            "has_exe_extension": url_lower.str.contains(
                r"\.exe(?:$|[/?#])",
                regex=True,
                na=False,
            ).astype(int),
            "has_html_extension": url_lower.str.contains(
                r"\.html?(?:$|[/?#])",
                regex=True,
                na=False,
            ).astype(int),
            "has_bin_extension": url_lower.str.contains(
                r"\.bin(?:$|[/?#])",
                regex=True,
                na=False,
            ).astype(int),
            "has_asp_extension": url_lower.str.contains(
                r"\.aspx?(?:$|[/?#])",
                regex=True,
                na=False,
            ).astype(int),
        }
    )

    # Combine all feature groups.
    feature_df = pd.concat(
        [
            base_df.reset_index(drop=True),
            component_df.reset_index(drop=True),
            extension_df.reset_index(drop=True),
        ],
        axis=1,
    )

    if len(FEATURE_NAMES) != 48:
        raise ValueError(
            f"Expected 48 features, found {len(FEATURE_NAMES)}"
        )

    if feature_df.shape[1] != 48:
        raise ValueError(
            f"Generated {feature_df.shape[1]} features "
            "instead of 48"
        )

    if feature_df.columns.tolist() != FEATURE_NAMES:
        raise ValueError(
            "Feature column order does not match "
            "the canonical enhanced schema"
        )

    missing_values = (
        feature_df.isnull().sum().sum()
    )

    if missing_values:
        raise ValueError(
            f"Found {missing_values} missing feature values"
        )

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

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        output_path,
        index=False,
    )

    print(f"Base features: {len(BASE_FEATURE_NAMES)}")
    print(
        f"Component features: "
        f"{len(COMPONENT_FEATURE_NAMES)}"
    )
    print(
        f"Total features: "
        f"{len(FEATURE_NAMES)}"
    )
    print(
        f"Output rows: "
        f"{len(result_df):,}"
    )

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

    print(f"\nOutput: {output_path}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
