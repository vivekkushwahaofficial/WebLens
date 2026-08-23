from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    """Risk assessment derived from the ML malicious probability."""

    risk_score: int
    verdict: str


def assess_risk(
    *,
    malicious_probability: float,
) -> RiskAssessment:
    """Convert malicious probability into a product risk assessment."""

    probability = min(
        max(malicious_probability, 0.0),
        1.0,
    )

    risk_score = round(probability * 100)

    if risk_score >= 70:
        verdict = "HIGH_RISK"
    elif risk_score >= 40:
        verdict = "MEDIUM_RISK"
    else:
        verdict = "LOW_RISK"

    return RiskAssessment(
        risk_score=risk_score,
        verdict=verdict,
    )
