"""
Aggregated Integrations Overview API
Combines data from Scapy (network), Flower (FL), Suricata (IDS), and Grafana (viz) modules.
"""
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status

# Import module-level singletons to avoid heavy re-instantiation
from integrations.network_monitoring.scapy_integration import network_monitor
from integrations.ml_models.flower_fl_integration import flower_manager
from integrations.security_tools.suricata_integration import suricata_ids
from integrations.visualization.grafana_integration import grafana_metrics

router = APIRouter(prefix="/api/integrations", tags=["Integrations Overview"])


def get_integrations_snapshot() -> Dict[str, Any]:
    # Network snapshot
    net = network_monitor.capture_packets()
    anomalies = network_monitor.detect_anomalies()

    # Flower snapshot (simulate a step, consistent with module design)
    fl = flower_manager.simulate_fl_round()
    clients = flower_manager.get_client_metrics()

    # Suricata snapshot
    alerts = suricata_ids.generate_alerts()
    rules = suricata_ids.get_rule_statistics()

    # Grafana snapshot (lightweight subset)
    dashboards = grafana_metrics.dashboards
    timeseries = grafana_metrics.time_series

    return {
        "network": {"packets": net, "anomalies": anomalies},
        "flower": {"status": fl, "clients": clients},
        "suricata": {"alerts": alerts, "rules": rules},
        "grafana": {
            "dashboards": dashboards,
            "metrics": {
                "fl_accuracy": timeseries.get("fl_accuracy", [])[-5:],
                "threat_count": timeseries.get("threat_count", [])[-5:],
            },
        },
    }


@router.get("/overview")
async def integrations_overview() -> Dict[str, Any]:
    """Return a combined snapshot and normalized integrations list for UI/tests."""
    snapshot = get_integrations_snapshot()
    integrations = [
        {
            "name": "Scapy",
            "type": "network_monitoring",
            "status": "active",
            "packets": snapshot.get("network", {}).get("packets", {}).get("total_packets", 0),
        },
        {
            "name": "Flower",
            "type": "federated_learning",
            "status": "active",
            "clients": len(snapshot.get("flower", {}).get("clients", [])),
        },
        {
            "name": "Suricata",
            "type": "intrusion_detection",
            "status": "active",
            "alerts": len(snapshot.get("suricata", {}).get("alerts", [])),
        },
        {
            "name": "Grafana",
            "type": "visualization",
            "status": "online",
            "dashboards": len(snapshot.get("grafana", {}).get("dashboards", [])),
        },
    ]
    return {"snapshot": snapshot, "integrations": integrations}


@router.post("/refresh")
async def integrations_refresh(request: Request) -> Dict[str, Any]:
    """Trigger a refresh and return the latest snapshot. RBAC: admin/operator."""
    user = getattr(request.state, "user", None)
    role = user.get("role") if isinstance(user, dict) else None
    if role not in {"admin", "operator"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return {"snapshot": get_integrations_snapshot()}
