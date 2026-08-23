from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    """Result of the initial rule-based risk assessment."""

    risk_score: int
    verdict: str


def assess_risk(
    *,
    url_length: int,
    uses_ip_address: bool,
    has_suspicious_keyword: bool,
) -> RiskAssessment:
    """Calculate an initial risk score from basic URL signals."""

    score = 0

    if url_length > 100:
        score += 20

    if uses_ip_address:
        score += 40

    if has_suspicious_keyword:
        score += 30

    score = min(score, 100)

    if score >= 70:
        verdict = "HIGH_RISK"
    elif score >= 40:
        verdict = "MEDIUM_RISK"
    else:
        verdict = "LOW_RISK"

    return RiskAssessment(
        risk_score=score,
        verdict=verdict,
    )