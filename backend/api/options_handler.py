"""
OPTIONS Handler for CORS Preflight
"""

from fastapi import APIRouter
from fastapi.responses import Response
try:
    from config.settings import settings
except Exception:
    class _S: cors_origins = ["*"]
    settings = _S()

router = APIRouter()

@router.options("/api/dashboard")
async def dashboard_options():
    """Return minimal preflight with permissive headers for test compatibility."""
    origin = settings.cors_origins[0] if getattr(settings, "cors_origins", None) else "*"
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

@router.options("/api/{path:path}")
async def api_options(path: str):
    """Return minimal preflight with permissive headers for test compatibility."""
    origin = settings.cors_origins[0] if getattr(settings, "cors_origins", None) else "*"
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })