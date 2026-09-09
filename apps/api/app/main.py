from fastapi import FastAPI

from app.routes.analyze import router as analyze_router
from app.routes.health import router as health_router


app = FastAPI(
    title="WebLens API",
    version="0.1.0",
    description="Real-time phishing and malicious URL early-warning API.",
)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    analyze_router,
    prefix="/api/v1",
)