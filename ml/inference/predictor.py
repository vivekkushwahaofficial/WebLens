from pathlib import Path
import re

import joblib
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
from ml.preprocessing.generate_enhanced_features import (
    COMPONENT_FEATURE_NAMES,
    EXTENSION_FEATURE_NAMES,
    EXCLUDED_BASE_FEATURES,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "weblens_random_forest.joblib"
)

FEATURE_SCHEMA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "feature_schema.joblib"
)

FEATURE_NAMES = [
    feature
    for feature in BASE_FEATURE_NAMES
    if feature not in EXCLUDED_BASE_FEATURES
] + COMPONENT_FEATURE_NAMES + EXTENSION_FEATURE_NAMES

class URLPredictor:
    """Load the WebLens model and predict URL classes."""

    def __init__(self) -> None:
        """Load model and validate its feature schema."""

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        if not FEATURE_SCHEMA_PATH.exists():
            raise FileNotFoundError(
                f"Feature schema not found: "
                f"{FEATURE_SCHEMA_PATH}"
            )

        self.model = joblib.load(MODEL_PATH)
        self.feature_schema = joblib.load(
            FEATURE_SCHEMA_PATH
        )

        self._validate_schema()

    def _validate_schema(self) -> None:
        """Ensure inference uses exactly the training schema."""

        if self.feature_schema != FEATURE_NAMES:
            raise ValueError(
                "Feature schema mismatch between "
                "training and inference."
            )

        if len(self.feature_schema) != 48:
            raise ValueError(
                f"Expected 48 features, found "
                f"{len(self.feature_schema)}"
            )

    def extract_features(self, url: str) -> list[float]:
        """Extract the exact 46 features used during training."""

        base_features = extract_url_features(url)

        base_vector = features_to_vector(
            base_features
        )

        component_features = (
            extract_url_component_features(url)
        )

        # Remove protocol-dependent features.
        base_vector = [
            value
            for name, value in zip(
                BASE_FEATURE_NAMES,
                base_vector,
            )
            if name not in EXCLUDED_BASE_FEATURES
        ]

        component_vector = [
            component_features[name]
            for name in COMPONENT_FEATURE_NAMES
        ]

        url_lower = url.lower()

        extension_features = {
            "has_exe_extension": int(
                re.search(
                    r"\.exe(?:$|[/?#])",
                    url_lower,
                )
                is not None
            ),
            "has_html_extension": int(
                re.search(
                    r"\.html?(?:$|[/?#])",
                    url_lower,
                )
                is not None
            ),
            "has_bin_extension": int(
                re.search(
                    r"\.bin(?:$|[/?#])",
                    url_lower,
                )
                is not None
            ),
            "has_asp_extension": int(
                re.search(
                    r"\.aspx?(?:$|[/?#])",
                    url_lower,
                )
                is not None
            ),
        }

        extension_vector = [
            extension_features[name]
            for name in EXTENSION_FEATURE_NAMES
        ]

        return (
            base_vector
            + component_vector
            + extension_vector
        )

    def predict(self, url: str) -> dict:
        """Predict the class of a URL."""

        features = self.extract_features(url)

        feature_df = pd.DataFrame(
            [features],
            columns=self.feature_schema,
        )

        prediction = self.model.predict(
            feature_df
        )[0]

        probabilities = self.model.predict_proba(
            feature_df
        )[0]

        class_probabilities = {
            class_name: float(probability)
            for class_name, probability in zip(
                self.model.classes_,
                probabilities,
            )
        }

        confidence = max(
            class_probabilities.values()
        )

        return {
            "url": url,
            "prediction": prediction,
            "confidence": float(confidence),
            "probabilities": class_probabilities,
        }


def main() -> None:
    """Run a simple inference demonstration."""

    predictor = URLPredictor()

    test_urls = [
        "https://www.google.com",
        "https://example.com/login?id=123",
        "http://192.168.1.10/verify/account?password=123",
    ]

    for url in test_urls:
        result = predictor.predict(url)

        print("\n" + "=" * 70)
        print(f"URL: {result['url']}")
        print(f"Prediction: {result['prediction']}")
        print(
            f"Confidence: "
            f"{result['confidence']:.4f}"
        )

        print("Probabilities:")

        for class_name, probability in (
            result["probabilities"].items()
        ):
            print(
                f"  {class_name}: "
                f"{probability:.4f}"
            )


if __name__ == "__main__":
    main()
