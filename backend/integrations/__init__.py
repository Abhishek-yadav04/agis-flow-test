"""
GitHub Project Integrations for AgisFL Enterprise
Real-time data integrations from top open-source security projects
"""

from .network_monitoring.scapy_integration import router as scapy_router
from .ml_models.flower_fl_integration import router as flower_router  
from .security_tools.suricata_integration import router as suricata_router
from .visualization.grafana_integration import router as grafana_router

# Export all routers for easy integration
__all__ = [
    'scapy_router',
    'flower_router', 
    'suricata_router',
    'grafana_router'
]