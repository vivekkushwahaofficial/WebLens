import re
from typing import Dict, List


# Canonical feature order used by both training and inference.
FEATURE_NAMES: List[str] = [
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
    "has_http",
    "has_https",
    "has_ip_address",
    "has_at_symbol",
    "has_percent_encoding",
    "has_login",
    "has_signin",
    "has_verify",
    "has_account",
    "has_update",
    "has_secure",
    "has_bank",
    "has_password",
    "has_confirm",
]


SUSPICIOUS_TERMS = (
    "login",
    "signin",
    "verify",
    "account",
    "update",
    "secure",
    "bank",
    "password",
    "confirm",
)


def extract_url_features(url: str) -> Dict[str, int]:
    """
    Extract explainable lexical and structural URL features.
    """

    url = str(url).strip()

    features = {
        "url_length": len(url),
        "digit_count": len(re.findall(r"\d", url)),
        "letter_count": len(re.findall(r"[A-Za-z]", url)),
        "special_char_count": len(
            re.findall(r"[^A-Za-z0-9]", url)
        ),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "slash_count": url.count("/"),
        "question_count": url.count("?"),
        "equals_count": url.count("="),
        "ampersand_count": url.count("&"),
        "at_count": url.count("@"),
        "percent_count": url.count("%"),
        "underscore_count": url.count("_"),
        "has_http": int(url.lower().startswith("http://")),
        "has_https": int(url.lower().startswith("https://")),
        "has_ip_address": int(
            bool(
                re.match(
                    r"^(?:https?://)?(?:\d{1,3}\.){3}\d{1,3}",
                    url,
                    re.IGNORECASE,
                )
            )
        ),
        "has_at_symbol": int("@" in url),
        "has_percent_encoding": int("%" in url),
    }

    lowercase_url = url.lower()

    for term in SUSPICIOUS_TERMS:
        features[f"has_{term}"] = int(
            term in lowercase_url
        )

    return features


def features_to_vector(features: Dict[str, int]) -> List[int]:
    """
    Convert a feature dictionary into the canonical ML feature order.
    """

    missing_features = [
        name for name in FEATURE_NAMES
        if name not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    return [features[name] for name in FEATURE_NAMES]
