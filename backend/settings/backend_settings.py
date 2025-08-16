"""
Backend Settings Manager
Real-time configuration management with live updates
"""

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import json
import os

router = APIRouter(prefix="/api/settings", tags=["Backend Settings"])

class SystemSettings(BaseModel):
    fl_strategy: str = "FedAvg"
    learning_rate: float = 0.001
    batch_size: int = 32
    num_rounds: int = 100
    client_fraction: float = 0.8
    threat_threshold: float = 0.7
    monitoring_interval: int = 5
    log_level: str = "INFO"
    auto_response: bool = True
    military_mode: bool = True

class BackendSettingsManager:
    def __init__(self):
        self.settings_file = "data/system_settings.json"
        self.current_settings = SystemSettings()
        
    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings.model_dump(), f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

settings_manager = BackendSettingsManager()

@router.get("/current")
async def get_current_settings() -> Dict[str, Any]:
    return {"settings": settings_manager.current_settings.model_dump()}

@router.post("/update")
async def update_settings(settings: SystemSettings, request: Request) -> Dict[str, Any]:
    # Only admin can update backend settings
    user = getattr(request.state, "user", None)
    role = user.get("role") if isinstance(user, dict) else None
    if role not in {"admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    settings_manager.current_settings = settings
    settings_manager.save_settings()
    return {"success": True, "settings": settings.model_dump()}