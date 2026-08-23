from app.services.risk_assessment import assess_risk


def test_low_risk() -> None:
    assessment = assess_risk(
        malicious_probability=0.10,
    )

    assert assessment.risk_score == 10
    assert assessment.verdict == "LOW_RISK"


def test_medium_risk() -> None:
    assessment = assess_risk(
        malicious_probability=0.50,
    )

    assert assessment.risk_score == 50
    assert assessment.verdict == "MEDIUM_RISK"


def test_high_risk() -> None:
    assessment = assess_risk(
        malicious_probability=0.90,
    )

    assert assessment.risk_score == 90
    assert assessment.verdict == "HIGH_RISK"


def test_risk_score_is_bounded() -> None:
    assessment = assess_risk(
        malicious_probability=1.50,
    )

    assert assessment.risk_score == 100


def test_negative_probability_is_bounded() -> None:
    assessment = assess_risk(
        malicious_probability=-0.50,
    )

    assert assessment.risk_score == 0
