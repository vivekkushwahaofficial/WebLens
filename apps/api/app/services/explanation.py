def generate_reasons(
    *,
    prediction: str,
    confidence: float,
) -> list[str]:
    """Generate human-readable reasons from the ML prediction."""

    if prediction == "phishing":
        return [
            "The ML model classified this URL as phishing."
        ]

    if prediction == "malware":
        return [
            "The ML model classified this URL as malware."
        ]

    if prediction == "defacement":
        return [
            "The ML model classified this URL as defacement."
        ]

    return [
        "The ML model classified this URL as benign."
    ]
