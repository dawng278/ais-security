from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import allowed_cors_origins, settings
from app.api import firewall, redteam, grading, dashboard, benchmark, arena, evidence, lineage
from app.api import security_v1
from app.operational.errors import GatewayException
from app.api.security_v1 import error_response


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gradingguard-ai"}


@app.middleware("http")
async def enforce_security_request_size(request: Request, call_next):
    if request.url.path.startswith("/api/v1/security"):
        content_length = request.headers.get("content-length")
        try:
            too_large = bool(content_length and int(content_length) > settings.max_request_body_chars)
        except ValueError:
            too_large = True
        if too_large:
            return JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": "Request is too large.",
                        "retryable": False,
                        "correlation_id": request.headers.get("x-correlation-id"),
                    }
                },
            )
    return await call_next(request)


@app.exception_handler(GatewayException)
def handle_gateway_exception(_request, exc: GatewayException):
    return error_response(exc)


app.include_router(firewall.router, prefix="/api/firewall", tags=["firewall"])
app.include_router(redteam.router, prefix="/api/redteam", tags=["redteam"])
app.include_router(grading.router, prefix="/api/grade", tags=["grading"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(benchmark.router, prefix="/api/benchmark", tags=["benchmark"])
app.include_router(arena.router, prefix="/api/arena", tags=["arena"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"])
app.include_router(lineage.router, prefix="/api/lineage", tags=["lineage"])
app.include_router(security_v1.router, prefix="/api/v1/security", tags=["security-v1"])
