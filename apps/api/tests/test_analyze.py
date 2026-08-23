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
    assert isinstance(data["risk_score"], int)
    assert 0 <= data["risk_score"] <= 100

    assert data["verdict"] in {
        "LOW_RISK",
        "MEDIUM_RISK",
        "HIGH_RISK",
    }

    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0

    assert isinstance(data["reasons"], list)
    assert len(data["reasons"]) >= 1

    assert all(
        isinstance(reason, str)
        for reason in data["reasons"]
    )


def test_analyze_ip_address_url() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"url": "http://192.168.1.10"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["url"] == "http://192.168.1.10/"
    assert isinstance(data["risk_score"], int)
    assert 0 <= data["risk_score"] <= 100

    assert data["verdict"] in {
        "LOW_RISK",
        "MEDIUM_RISK",
        "HIGH_RISK",
    }

    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0

    assert isinstance(data["reasons"], list)
    assert len(data["reasons"]) >= 1


def test_analyze_invalid_url() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422
