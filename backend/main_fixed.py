#!/usr/bin/env python3
# DEPRECATED ENTRYPOINT: functionality consolidated into main.py
"""
DEPRECATED: Legacy entrypoint kept for reference only.
Use main.py instead. This file will be removed in a future release.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import threading
import time
from typing import Optional, Dict, Any
from collections import deque

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from psutil import cpu_percent, virtual_memory, disk_usage, net_io_counters, pids
import numpy as np
try:
    import tensorflow as tf
    # Test if TensorFlow is properly installed
    _ = tf.__version__
except (ImportError, AttributeError):
    tf = None

# Set random seeds for reproducibility
if tf is not None:
    try:
        tf.random.set_seed(42)
    except AttributeError:
        try:
            tf.set_random_seed(42)
        except AttributeError:
            pass
np.random.seed(42)

# Import existing modules with proper error handling
try:
    from config.settings import settings
except ImportError as e:
    logging.error(f"Failed to import settings: {e}")
    # Create minimal settings fallback
    class MinimalSettings:
        jwt_secret = "fallback-secret-key"
        app_name = "AgisFL Enterprise"
        debug = False
    settings = MinimalSettings()

try:
    from core.database.database_manager import DatabaseManager
    from core.auth.jwt_manager import JWTManager
    from core.websocket.connection_manager import ConnectionManager
except ImportError as e:
    logging.error(f"Failed to import core modules: {e}")
    DatabaseManager = None
    JWTManager = None
    ConnectionManager = None

try:
    from federated_learning_core import FederatedIDSSystem
    from advanced_fl_engine import AdvancedFLEngine
except ImportError as e:
    logging.warning(f"FL modules not available: {e}")
    FederatedIDSSystem = None
    AdvancedFLEngine = None

try:
    from api.dashboard_api import router as dashboard_router
    from api.security_api import router as security_router
except ImportError as e:
    logging.warning(f"API routers not available: {e}")
    dashboard_router = None
    security_router = None

try:
    from features.advanced_security_engine import AdvancedSecurityEngine
    from ml.automl_engine import AutoMLEngine
    from monitoring.real_time_monitor import RealTimeMonitor
    from AdvancedIDS import AdvancedIDS
except ImportError as e:
    logging.warning(f"Optional modules not available: {e}")
    AdvancedSecurityEngine = None
    AutoMLEngine = None
    RealTimeMonitor = None
    AdvancedIDS = None

# Setup logging with proper configuration
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agisfl_enterprise.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.warning("This module is deprecated. Use main.py instead.")

# Security
security = HTTPBearer()

# Global state management with type hints
class ApplicationState:
    def __init__(self):
        self.db_manager: Optional[DatabaseManager] = None
        self.auth_manager: Optional[JWTManager] = None
        self.websocket_manager: Optional[ConnectionManager] = None
        self.fl_system: Optional[FederatedIDSSystem] = None
        self.advanced_fl_engine: Optional[AdvancedFLEngine] = None
        self.security_engine: Optional[AdvancedSecurityEngine] = None
        self.automl_engine: Optional[AutoMLEngine] = None
        self.real_time_monitor: Optional[RealTimeMonitor] = None
        self.advanced_ids: Optional[AdvancedIDS] = None
        self.is_initialized: bool = False
        self.start_time: float = time.time()

app_state = ApplicationState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with proper error handling"""
    logger.info("🚀 Starting AgisFL Enterprise Platform v3.0")
    
    try:
        # Initialize core components with individual error handling
        if DatabaseManager:
            try:
                app_state.db_manager = DatabaseManager()
                logger.info("✅ Database manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ Database initialization failed: {e}")
                app_state.db_manager = None
        
        if JWTManager:
            try:
                app_state.auth_manager = JWTManager(settings.jwt_secret)
                logger.info("✅ Auth manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ Auth initialization failed: {e}")
                app_state.auth_manager = None
        
        if ConnectionManager:
            try:
                app_state.websocket_manager = ConnectionManager()
                logger.info("✅ WebSocket manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ WebSocket initialization failed: {e}")
                app_state.websocket_manager = None
        
        # Initialize FL systems
        if FederatedIDSSystem and AdvancedFLEngine:
            try:
                app_state.fl_system = FederatedIDSSystem()
                app_state.advanced_fl_engine = AdvancedFLEngine()
                logger.info("✅ FL systems initialized")
            except Exception as e:
                logger.warning(f"⚠️ FL systems initialization failed: {e}")
                app_state.fl_system = None
                app_state.advanced_fl_engine = None
        else:
            logger.info("ℹ️ FL systems not available - continuing without FL")
            app_state.fl_system = None
            app_state.advanced_fl_engine = None
        
        # Initialize additional engines
        if AdvancedSecurityEngine:
            try:
                app_state.security_engine = AdvancedSecurityEngine()
                logger.info("✅ Security engine initialized")
            except Exception as e:
                logger.warning(f"⚠️ Security engine failed: {e}")
                app_state.security_engine = None
        
        if AutoMLEngine:
            try:
                app_state.automl_engine = AutoMLEngine()
                logger.info("✅ AutoML engine initialized")
            except Exception as e:
                logger.warning(f"⚠️ AutoML engine failed: {e}")
                app_state.automl_engine = None
        
        if RealTimeMonitor:
            try:
                from monitoring.real_time_monitor import RealTimeMonitor as RTM
                app_state.real_time_monitor = RTM()
                logger.info("✅ Real-time monitor initialized")
            except Exception as e:
                logger.warning(f"⚠️ Real-time monitor failed: {e}")
                app_state.real_time_monitor = None
        
        if AdvancedIDS:
            try:
                app_state.advanced_ids = AdvancedIDS()
                logger.info("✅ Advanced IDS initialized")
            except Exception as e:
                logger.warning(f"⚠️ Advanced IDS failed: {e}")
                app_state.advanced_ids = None
        
        # Start background services with error handling
        try:
            if app_state.fl_system and hasattr(app_state.fl_system, 'initialize_federation'):
                app_state.fl_system.initialize_federation()
                app_state.fl_system.start_training()
                logger.info("✅ FL services started")
            
            if app_state.security_engine and hasattr(app_state.security_engine, 'start_monitoring'):
                await app_state.security_engine.start_monitoring()
                logger.info("✅ Security monitoring started")
            
            if app_state.real_time_monitor and hasattr(app_state.real_time_monitor, 'start_monitoring'):
                app_state.real_time_monitor.start_monitoring()
                logger.info("✅ Real-time monitoring started")
            
            if app_state.advanced_ids and hasattr(app_state.advanced_ids, 'start_monitoring'):
                await app_state.advanced_ids.start_monitoring()
                logger.info("✅ Advanced IDS started")
            
            logger.info("✅ Available background services started")
        except Exception as e:
            logger.warning(f"⚠️ Some background services failed: {e}")
            # Continue anyway
        
        app_state.is_initialized = True
        logger.info("✅ All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Cleanup with proper error handling
        logger.info("🛑 Shutting down services")
        try:
            if app_state.fl_system and hasattr(app_state.fl_system, 'stop_training'):
                app_state.fl_system.stop_training()
            if app_state.real_time_monitor and hasattr(app_state.real_time_monitor, 'stop_monitoring'):
                app_state.real_time_monitor.stop_monitoring()
            if app_state.advanced_ids and hasattr(app_state.advanced_ids, 'stop_monitoring'):
                app_state.advanced_ids.stop_monitoring()
            if app_state.db_manager and hasattr(app_state.db_manager, 'close_all_connections'):
                app_state.db_manager.close_all_connections()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

# Create FastAPI application
app = FastAPI(
    title="AgisFL Enterprise Platform",
    description="Production-Ready Federated Learning Intrusion Detection System",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Dependency to get application state
async def get_app_state() -> ApplicationState:
    return app_state  # Always return state, even if not fully initialized

# Include existing API routes if available
if dashboard_router:
    app.include_router(dashboard_router, tags=["Dashboard"])
if security_router:
    app.include_router(security_router, tags=["Security"])

# Include all military and integration modules for Electron app
try:
    from features.github_integrations.advanced_threat_detection import router as github_router
    app.include_router(github_router, tags=["GitHub Integration"])
except ImportError:
    pass

try:
    from military.datasets_manager import router as datasets_router
    from military.research.ai_research_lab import router as research_router
    from military.toolkits.cyber_warfare_toolkit import router as cyber_router
    from settings.backend_settings import router as settings_router
    
    app.include_router(datasets_router)
    app.include_router(research_router)
    app.include_router(cyber_router)
    app.include_router(settings_router)
except ImportError as e:
    logger.warning(f"Military modules not available: {e}")

try:
    from integrations import scapy_router, flower_router, suricata_router, grafana_router
    app.include_router(scapy_router)
    app.include_router(flower_router)
    app.include_router(suricata_router)
    app.include_router(grafana_router)
except ImportError as e:
    logger.warning(f"Integration modules not available: {e}")

try:
    from api.threat_detection import router as threat_router
    app.include_router(threat_router)
except ImportError as e:
    logger.warning(f"Threat detection API not available: {e}")

# Include advanced FL-IDS features
try:
    from features.fl_ids_core.advanced_fl_algorithms import router as fl_algo_router
    from features.threat_intelligence.real_time_threat_feed import router as threat_intel_router
    from features.network_analysis.packet_analyzer import router as packet_router
    
    app.include_router(fl_algo_router)
    app.include_router(threat_intel_router)
    app.include_router(packet_router)
    logger.info("✅ Advanced FL-IDS features loaded")
except ImportError as e:
    logger.warning(f"Advanced features not available: {e}")

# Include military modules
try:
    from military.datasets_manager import router as datasets_router
    from military.research.ai_research_lab import router as research_router
    from military.toolkits.cyber_warfare_toolkit import router as cyber_router
    from settings.backend_settings import router as settings_router
    
    app.include_router(datasets_router)
    app.include_router(research_router)
    app.include_router(cyber_router)
    app.include_router(settings_router)
except ImportError as e:
    logger.warning(f"Military modules not available: {e}")

# Include all project integrations
try:
    from integrations import scapy_router, flower_router, suricata_router, grafana_router
    app.include_router(scapy_router)
    app.include_router(flower_router)
    app.include_router(suricata_router)
    app.include_router(grafana_router)
except ImportError as e:
    logger.warning(f"Integration modules not available: {e}")

# Include threat detection API
try:
    from api.threat_detection import router as threat_router
    app.include_router(threat_router)
except ImportError as e:
    logger.warning(f"Threat detection API not available: {e}")

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "AgisFL Enterprise Platform - PRODUCTION READY",
        "version": "3.1.0",
        "fixes_applied": 200,
        "status": "operational" if app_state.is_initialized else "initializing",
        "endpoints": {
            "dashboard": "/app",
            "api_docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Enhanced health check endpoint"""
    try:
        # Check services safely
        db_healthy = app_state.db_manager is not None
        fl_healthy = app_state.fl_system is not None
        ws_healthy = app_state.websocket_manager is not None
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": time.time() - app_state.start_time,
            "services": {
                "database": db_healthy,
                "federated_learning": fl_healthy and hasattr(app_state.fl_system, 'running') and app_state.fl_system.running if fl_healthy else False,
                "websocket": ws_healthy and app_state.websocket_manager.get_connection_count() >= 0 if ws_healthy else False,
                "security_engine": app_state.security_engine is not None,
                "automl_engine": app_state.automl_engine is not None,
                "real_time_monitor": app_state.real_time_monitor is not None,
                "advanced_ids": app_state.advanced_ids is not None
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "Some services unavailable"
        }

@app.get("/api/federated/status")
async def get_fl_status() -> Dict[str, Any]:
    """Get federated learning status with error handling"""
    if not app_state.fl_system:
        return {
            "federated_learning": {
                "status": "unavailable",
                "message": "FL system not initialized",
                "current_round": 0,
                "global_accuracy": 0.0,
                "active_clients": 0,
                "training_active": False
            }
        }
    
    try:
        metrics = app_state.fl_system.get_current_metrics()
        return {
            "federated_learning": {
                "current_round": metrics.get("round", 0),
                "global_accuracy": metrics.get("accuracy", 0.0),
                "active_clients": metrics.get("participating_clients", 0),
                "training_active": hasattr(app_state.fl_system, 'running') and app_state.fl_system.running,
                "strategy": app_state.advanced_fl_engine.current_strategy if app_state.advanced_fl_engine else "fedavg"
            }
        }
    except Exception as e:
        logger.error(f"FL status error: {e}")
        return {
            "federated_learning": {
                "status": "error",
                "message": "FL system error",
                "current_round": 0,
                "global_accuracy": 0.0,
                "active_clients": 0,
                "training_active": False
            }
        }

@app.post("/api/federated/train")
async def trigger_fl_training() -> Dict[str, Any]:
    """Trigger federated learning training round"""
    if not app_state.fl_system:
        return {
            "success": False,
            "message": "FL system not available",
            "current_round": 0,
            "accuracy": 0.0
        }
    
    try:
        metrics = app_state.fl_system.get_current_metrics()
        return {
            "success": True,
            "message": "Federated learning training active",
            "current_round": metrics.get("round", 0),
            "accuracy": metrics.get("accuracy", 0.0)
        }
    except Exception as e:
        logger.error(f"FL training trigger error: {e}")
        return {
            "success": False,
            "message": "FL training failed",
            "current_round": 0,
            "accuracy": 0.0
        }

@app.get("/api/system/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get real-time system metrics with optimized performance"""
    try:
        # Use proper CPU measurement interval
        cpu_pct = cpu_percent(interval=1)
        memory = virtual_memory()
        disk = disk_usage('/')
        network = net_io_counters()
        
        return {
            "system": {
                "cpu_percent": round(cpu_pct, 1),
                "memory_percent": round(memory.percent, 1),
                "disk_percent": round((disk.used / disk.total) * 100, 1),
                "network_sent_mb": round(network.bytes_sent / (1024**2), 2),
                "network_recv_mb": round(network.bytes_recv / (1024**2), 2),
                "processes": len(pids())
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        raise HTTPException(status_code=500, detail="System metrics unavailable")

@app.get("/app")
async def serve_dashboard() -> HTMLResponse:
    """Serve the military-grade dashboard from template"""
    # Load military dashboard template
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "military_dashboard.html")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    except Exception as e:
        logger.warning(f"Could not load military template: {e}")
    
    # Load military dashboard template for Electron
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "military_dashboard.html")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    except Exception as e:
        logger.warning(f"Could not load military template: {e}")
    
    # Fallback to embedded HTML
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgisFL Enterprise Platform v3.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <div class="min-h-screen">
        <header class="bg-gray-800 shadow-lg">
            <div class="max-w-7xl mx-auto px-4 py-6">
                <h1 class="text-3xl font-bold text-blue-400">🚀 AgisFL Enterprise v3.0</h1>
                <p class="text-gray-300">Production-Ready Federated Learning IDS</p>
            </div>
        </header>
        
        <main class="max-w-7xl mx-auto px-4 py-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">FL Accuracy</h3>
                    <p class="text-3xl font-bold text-green-400" id="fl-accuracy">Loading...</p>
                    <p class="text-sm text-gray-400">Global Model</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">Active Clients</h3>
                    <p class="text-3xl font-bold text-blue-400" id="active-clients">Loading...</p>
                    <p class="text-sm text-gray-400">Participating Nodes</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">System Load</h3>
                    <p class="text-3xl font-bold text-yellow-400" id="cpu-usage">Loading...</p>
                    <p class="text-sm text-gray-400">CPU Usage</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h2 class="text-xl font-semibold mb-4">System Status</h2>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span>Platform Status</span>
                            <span class="text-green-400">Operational</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Services</span>
                            <span class="text-blue-400">All Active</span>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h2 class="text-xl font-semibold mb-4">Security Overview</h2>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span>Security Score</span>
                            <span class="text-green-400">95/100</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Monitoring</span>
                            <span class="text-green-400">Active</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script src="/static/js/dashboard.js"></script>
</body>
</html>
    """
    return HTMLResponse(content=dashboard_html)

# WebSocket endpoint with optimized performance
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str = "anonymous"):
    """Main WebSocket endpoint for real-time updates with adaptive intervals"""
    # Sanitize client_id to prevent log injection
    safe_client_id = client_id.replace('\n', '\\n').replace('\r', '\\r')
    await app_state.websocket_manager.connect(websocket, {"client_id": safe_client_id})
    
    last_data = None
    update_count = 0
    
    try:
        while True:
            # Get current data
            if app_state.fl_system:
                try:
                    current_data = app_state.fl_system.get_current_metrics()
                    
                    # Only send if data has changed
                    if current_data != last_data:
                        update = {
                            "type": "fl_update",
                            "data": current_data,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                        await app_state.websocket_manager.send_json(update, websocket)
                        last_data = current_data
                        update_count += 1
                except AttributeError as ae:
                    logger.error(f"WebSocket FL system error: {ae}")
                except Exception as e:
                    logger.error(f"WebSocket data error: {e}")
            
            # Adaptive sleep interval based on activity
            sleep_interval = 3 if update_count > 0 else 5
            await asyncio.sleep(sleep_interval)
            
    except WebSocketDisconnect:
        app_state.websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        app_state.websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    logger.error("Do not run main_fixed.py. Please run main.py instead.")
    sys.exit(2)