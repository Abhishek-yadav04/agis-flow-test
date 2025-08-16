"""
Admin Privilege API
Safe admin privilege management
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["Admin Privileges"])

try:
    from utils.admin_handler import admin_handler
    ADMIN_HANDLER_AVAILABLE = True
except ImportError:
    ADMIN_HANDLER_AVAILABLE = False
    logger.warning("Admin handler not available")

@router.get("/status")
async def get_admin_status():
    """Get current admin privilege status"""
    if not ADMIN_HANDLER_AVAILABLE:
        return {
            "is_admin": False,
            "platform": "unknown",
            "features_available": {"real_packet_capture": False},
            "capture_mode": "simulation"
        }
    
    try:
        return admin_handler.get_privilege_status()
    except Exception as e:
        logger.error(f"Admin status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-privileges")
async def request_admin_privileges():
    """Request admin privileges through dialog"""
    return {
        "status": "dialog_required",
        "message": "Please use the admin dialog in the dashboard to request privileges",
        "method": "uac_dialog",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/enable-simulation")
async def enable_simulation_mode():
    """Enable simulation mode for demonstration"""
    return {
        "status": "simulation_enabled",
        "message": "Simulation mode enabled - all features available for demonstration",
        "capture_mode": "simulation",
        "features_enabled": {
            "real_packet_capture": True,
            "system_level_monitoring": True,
            "network_interface_access": True,
            "process_monitoring": True
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }