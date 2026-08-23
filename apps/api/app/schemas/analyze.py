from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request body for URL analysis."""

    url: HttpUrl


class AnalyzeResponse(BaseModel):
    """Response returned after URL analysis."""

    url: str
    risk_score: int
    verdict: str
    confidence: float | None
    reasons: list[str]