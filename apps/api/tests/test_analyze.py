from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_safe_url() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["url"] == "https://example.com/"
    assert data["risk_score"] == 0
    assert data["verdict"] == "LOW_RISK"
    assert data["confidence"] is None
    assert data["reasons"] == [
        "No significant suspicious URL patterns detected"
    ]


def test_analyze_ip_address_url() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"url": "http://192.168.1.10"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_score"] == 40
    assert data["verdict"] == "MEDIUM_RISK"


def test_analyze_invalid_url() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422