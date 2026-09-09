from dataclasses import dataclass

from app.services.risk_assessment import RiskAssessment, assess_risk
from ml.inference.predictor import URLPredictor


@dataclass(frozen=True)
class URLFeatures:
    """ML inference signals returned for API explanation."""

    url_length: int
    uses_ip_address: bool
    has_suspicious_keyword: bool


_predictor = URLPredictor()


def analyze_url(url: str) -> tuple[dict, RiskAssessment]:
    """Analyze a URL using the finalized WebLens ML model."""

    prediction = _predictor.predict(url)

    probabilities = prediction["probabilities"]

    malicious_probability = (
        probabilities.get("phishing", 0.0)
        + probabilities.get("malware", 0.0)
        + probabilities.get("defacement", 0.0)
    )

    assessment = assess_risk(
        malicious_probability=malicious_probability,
    )

    return prediction, assessment
