from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import firewall, redteam, grading, dashboard


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gradingguard-ai"}


app.include_router(firewall.router, prefix="/api/firewall", tags=["firewall"])
app.include_router(redteam.router, prefix="/api/redteam", tags=["redteam"])
app.include_router(grading.router, prefix="/api/grade", tags=["grading"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
