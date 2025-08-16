"""
System Optimizer API
Real-time performance optimization endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimizer", tags=["System Optimizer"])

try:
    from core.optimizer import system_optimizer
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False
    logger.warning("System optimizer not available")

@router.get("/status")
async def get_optimizer_status():
    """Get system optimizer status"""
    if not OPTIMIZER_AVAILABLE:
        return {
            "is_running": False,
            "available": False,
            "message": "System optimizer not available"
        }
    
    try:
        return system_optimizer.get_optimization_status()
    except Exception as e:
        logger.error(f"Optimizer status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def force_optimization():
    """Force immediate system optimization"""
    if not OPTIMIZER_AVAILABLE:
        raise HTTPException(status_code=503, detail="System optimizer not available")
    
    try:
        result = system_optimizer.force_optimization()
        return {
            **result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Force optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_optimization_metrics():
    """Get optimization performance metrics"""
    if not OPTIMIZER_AVAILABLE:
        return {"metrics": [], "available": False}
    
    try:
        status = system_optimizer.get_optimization_status()
        return {
            "optimization_count": status.get("optimization_count", 0),
            "average_improvement": status.get("average_improvement", 0.0),
            "last_optimization": status.get("last_optimization"),
            "is_running": status.get("is_running", False),
            "thresholds": status.get("current_thresholds", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Optimization metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))