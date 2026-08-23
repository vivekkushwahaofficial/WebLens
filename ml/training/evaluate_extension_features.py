from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from ml.features.url_features import FEATURE_NAMES as BASE_FEATURE_NAMES
from ml.preprocessing.generate_enhanced_features import (
    COMPONENT_FEATURE_NAMES,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "url_enhanced_features.csv"
)

BASE_FEATURES = (
    BASE_FEATURE_NAMES
    + COMPONENT_FEATURE_NAMES
)

EXTENSION_FEATURES = [
    "has_exe_extension",
    "has_bin_extension",
    "has_dll_extension",
    "has_js_extension",
    "has_html_extension",
    "has_zip_extension",
    "has_asp_extension",
]

EXCLUDED_FEATURES = {
    "has_http",
    "has_https",
}

MODEL_FEATURES = [
    feature
    for feature in BASE_FEATURES
    if feature not in EXCLUDED_FEATURES
] + EXTENSION_FEATURES


def extract_hostname(url: str) -> str:
    """Extract a normalized hostname."""

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


def add_extension_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add URL extension indicator features."""

    result = df.copy()

    url = result["url"].astype(str).str.lower()

    result["has_exe_extension"] = (
        url.str.contains(
            r"\.exe(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_bin_extension"] = (
        url.str.contains(
            r"\.bin(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_dll_extension"] = (
        url.str.contains(
            r"\.dll(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_js_extension"] = (
        url.str.contains(
            r"\.js(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_html_extension"] = (
        url.str.contains(
            r"\.html?(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_zip_extension"] = (
        url.str.contains(
            r"\.zip(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    result["has_asp_extension"] = (
        url.str.contains(
            r"\.aspx?(?:$|[/?#])",
            regex=True,
            na=False,
        )
        .astype(int)
    )

    return result


def main() -> None:
    """Evaluate extension-aware features on unseen domains."""

    print("=" * 70)
    print("WebLens Extension Feature Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    df = add_extension_features(df)

    print(f"\nRows: {len(df):,}")
    print(f"Base features: {len(BASE_FEATURES)}")
    print(f"Experiment features: {len(MODEL_FEATURES)}")

    df["hostname"] = df["url"].apply(
        extract_hostname
    )

    hostname_class_counts = (
        df.groupby("hostname")["type"]
        .nunique()
    )

    single_class_hostnames = hostname_class_counts[
        hostname_class_counts == 1
    ].index

    domain_df = df[
        df["hostname"].isin(single_class_hostnames)
    ].copy()

    hostname_labels = (
        domain_df.groupby("hostname")["type"]
        .first()
        .reset_index()
    )

    train_hosts, test_hosts = train_test_split(
        hostname_labels,
        test_size=0.20,
        random_state=42,
        stratify=hostname_labels["type"],
    )

    train_host_set = set(
        train_hosts["hostname"]
    )

    test_host_set = set(
        test_hosts["hostname"]
    )

    if train_host_set & test_host_set:
        raise ValueError(
            "Domain leakage detected."
        )

    train_df = domain_df[
        domain_df["hostname"].isin(train_host_set)
    ]

    test_df = domain_df[
        domain_df["hostname"].isin(test_host_set)
    ]

    X_train = train_df[MODEL_FEATURES]
    X_test = test_df[MODEL_FEATURES]

    y_train = train_df["type"]
    y_test = test_df["type"]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    print("\nTraining Random Forest...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n" + "=" * 70)
    print("Extension Feature Results")
    print("=" * 70)

    print(
        f"\nAccuracy: "
        f"{accuracy_score(y_test, predictions):.4f}"
    )

    print(
        "Macro Precision: "
        f"{precision_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        "Macro Recall: "
        f"{recall_score(y_test, predictions, average='macro'):.4f}"
    )

    print(
        "Macro F1: "
        f"{f1_score(y_test, predictions, average='macro'):.4f}"
    )

    print("\nFeature Importances:")

    importance = pd.DataFrame(
        {
            "feature": MODEL_FEATURES,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    print(
        importance.head(20).to_string(
            index=False
        )
    )

    print("\nTraining rows:", f"{len(X_train):,}")
    print("Testing rows: ", f"{len(X_test):,}")
    print(
        "Shared hostnames:",
        len(train_host_set & test_host_set),
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
