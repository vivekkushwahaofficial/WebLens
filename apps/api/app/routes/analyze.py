from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import analyze_url
from app.services.explanation import generate_reasons


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a submitted URL and return its risk assessment."""

    prediction, assessment = analyze_url(str(request.url))

    reasons = generate_reasons(
        prediction=prediction["prediction"],
        confidence=prediction["confidence"],
    )

    return AnalyzeResponse(
        url=str(request.url),
        risk_score=assessment.risk_score,
        verdict=assessment.verdict,
        confidence=prediction["confidence"],
        reasons=reasons,
    )
