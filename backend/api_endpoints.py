#!/usr/bin/env python3
"""
Additional API Endpoints for GitHub Features
"""

from fastapi import HTTPException, Request, status
from typing import Dict, Any
try:
    from logging.structured import log_event  # type: ignore
except Exception:
    def log_event(*args, **kwargs):
        pass
import logging

logger = logging.getLogger(__name__)

def _extract_token(request: Request) -> str | None:
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None

def _verify_and_get_payload(request: Request) -> Dict[str, Any] | None:
    # Lazy import to avoid circulars
    try:
        from main import app_state  # type: ignore
    except Exception:
        return None
    token = _extract_token(request)
    if not token or not getattr(app_state, 'auth_manager', None):
        return None
    try:
        payload = app_state.auth_manager.verify_token(token)
        return payload
    except Exception:
        return None

def _require_role(payload: Dict[str, Any] | None, roles: set[str]):
    if not payload or payload.get("role") not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def setup_automl_endpoints(app):
    """Setup AutoML API endpoints"""
    
    @app.post("/api/automl/create")
    async def create_automl_experiment(request: Request, experiment_data: dict):
        """Create AutoML experiment"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "automl_create_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "researcher"})
        
        try:
            from ml.automl_engine import automl_engine
            
            exp_id = automl_engine.create_experiment(
                experiment_data.get("name", "AutoML Experiment"),
                experiment_data.get("dataset_type", "security"),
                experiment_data.get("algorithm", "auto")
            )
            
            return {"success": True, "experiment_id": exp_id}
        except Exception as e:
            logger.error(f"Create AutoML experiment error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/automl/start/{exp_id}")
    async def start_automl_experiment(request: Request, exp_id: str):
        """Start AutoML experiment"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "automl_start_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "researcher"})
        
        try:
            from ml.automl_engine import automl_engine
            result = automl_engine.start_experiment(exp_id)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Start AutoML experiment error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/datasets/upload")
    async def upload_dataset(request: Request):
        """Upload dataset"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "dataset_upload_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "data_engineer"})
        log_event("info", "dataset_upload_started", user=payload.get("username"))
        
        try:
            from ml.automl_engine import dataset_manager
            dataset_id = dataset_manager.upload_dataset("uploaded_dataset", "data", "csv")
            log_event("info", "dataset_upload_completed", dataset_id=dataset_id)
            return {"success": True, "dataset_id": dataset_id}
        except Exception as e:
            logger.error(f"Dataset upload error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/datasets/list")
    async def list_datasets(request: Request):
        """List available datasets"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "dataset_list_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "data_engineer", "researcher"})
        
        try:
            from ml.automl_engine import dataset_manager
            datasets = dataset_manager.get_datasets()
            return datasets
        except Exception as e:
            logger.error(f"List datasets error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def setup_attack_endpoints(app):
    """Setup attack simulation endpoints"""
    
    @app.post("/api/attack/start")
    async def start_attack_simulation(request: Request, attack_data: dict):
        """Start attack simulation"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "attack_start_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "security"})
        log_event("info", "attack_simulation_start", attack_type=attack_data.get("attack_type"))
        
        try:
            import importlib
            try:
                attack_mod = importlib.import_module("attack_simulation")
                get_attack_simulator = getattr(attack_mod, "get_attack_simulator")
            except Exception:
                log_event("warning", "attack_simulation_module_missing")
                raise HTTPException(status_code=503, detail="Attack simulation module unavailable")
            simulator = get_attack_simulator()
            
            result = simulator.start_simulation(
                attack_data.get("attack_type", "ddos"),
                attack_data.get("duration", 60),
                attack_data.get("intensity", "medium")
            )
            
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Attack simulation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/attack/stop")
    async def stop_attack_simulation(request: Request):
        """Stop attack simulation"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "attack_stop_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "security"})
        log_event("info", "attack_simulation_stop_request")
        
        try:
            import importlib
            try:
                attack_mod = importlib.import_module("attack_simulation")
                get_attack_simulator = getattr(attack_mod, "get_attack_simulator")
            except Exception:
                log_event("warning", "attack_simulation_module_missing")
                raise HTTPException(status_code=503, detail="Attack simulation module unavailable")
            simulator = get_attack_simulator()
            
            result = simulator.stop_simulation()
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Stop attack simulation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/attack/status")
    async def get_attack_status(request: Request):
        """Get attack simulation status"""
        payload = _verify_and_get_payload(request)
        if not payload:
            log_event("warning", "attack_status_unauthorized")
            raise HTTPException(status_code=401, detail="Authentication required")
        _require_role(payload, {"admin", "security", "observer"})
        
        try:
            import importlib
            try:
                attack_mod = importlib.import_module("attack_simulation")
                get_attack_simulator = getattr(attack_mod, "get_attack_simulator")
            except Exception:
                log_event("warning", "attack_simulation_module_missing")
                raise HTTPException(status_code=503, detail="Attack simulation module unavailable")
            simulator = get_attack_simulator()
            
            status = simulator.get_simulation_status()
            return {"success": True, "status": status}
        except Exception as e:
            logger.error(f"Get attack status error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def setup_all_endpoints(app):
    """Setup all GitHub feature endpoints"""
    setup_automl_endpoints(app)
    setup_attack_endpoints(app)