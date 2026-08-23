from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import analyze_url
from app.services.explanation import generate_reasons


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a submitted URL and return its risk assessment."""

    features, assessment = analyze_url(str(request.url))

    reasons = generate_reasons(
        url_length=features.url_length,
        uses_ip_address=features.uses_ip_address,
        has_suspicious_keyword=features.has_suspicious_keyword,
    )

    return AnalyzeResponse(
        url=str(request.url),
        risk_score=assessment.risk_score,
        verdict=assessment.verdict,
        confidence=None,
        reasons=reasons,
    )