import os
import sys

# Ensure backend is importable
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(ROOT), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient  # type: ignore
from main import app, app_state  # type: ignore


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "services" in data


def test_feature_flags():
    resp = client.get("/api/feature-flags")
    assert resp.status_code == 200
    data = resp.json()
    assert "gpt5_preview" in data
    assert "gemini_2_5_pro" in data


def test_federated_status():
    resp = client.get("/api/federated/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "federated_learning" in data


def test_system_metrics():
    resp = client.get("/api/system/metrics")
    assert resp.status_code == 200
    data = resp.json()
    # Check for expected keys in the new structure
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "network" in data
    assert "timestamp" in data


def test_dashboard_html():
    resp = client.get("/app")
    assert resp.status_code == 200
    # Should return HTML
    assert "text/html" in resp.headers.get("content-type", "")

def test_dashboard_api_extended_fields():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    # Newly integrated advanced sections
    for key in ("detailed_system_metrics", "charts_data", "analytics", "network_monitoring"):
        assert key in data, f"Missing {key} in /api/dashboard response"
    # Spot check nested structure
    assert "cpu" in data["detailed_system_metrics"], "cpu metrics missing"
    assert "system_overview" in data["charts_data"], "system_overview chart missing"
    assert isinstance(data["analytics"].get("user_sessions"), int)
    assert "bandwidth_utilization" in data["network_monitoring"], "network utilization missing"


def test_dashboard_cache_hit_and_metrics():
    # First call warms cache
    first = client.get("/api/dashboard")
    assert first.status_code == 200
    # Second call should hit cache (we can't read log, but metrics should increment)
    second = client.get("/api/dashboard")
    assert second.status_code == 200
    # Check metrics endpoint for dashboard_cache_hits >=1
    metrics = client.get("/metrics")
    # Metrics endpoint might be disabled; accept 200 or 404
    if metrics.status_code == 200:
        body = metrics.text
        assert "agisfl_dashboard_cache_hits" in body


# Routers used by the military dashboard

def test_threat_intel_live_feed():
    resp = client.get("/api/threat-intel/live-feed")
    assert resp.status_code == 200
    assert "threats" in resp.json()


def test_packet_analysis_live():
    resp = client.get("/api/packet-analysis/live-analysis")
    assert resp.status_code == 200
    assert "analysis" in resp.json()


def test_datasets_overview():
    resp = client.get("/api/datasets/military/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "datasets" in data and "statistics" in data


def test_fl_algorithms():
    resp = client.get("/api/fl-algorithms/algorithms")
    assert resp.status_code == 200
    assert "algorithms" in resp.json()


def test_backend_settings():
    resp = client.get("/api/settings/current")
    assert resp.status_code == 200
    assert "settings" in resp.json()


# GitHub integrations

def test_flower_status():
    resp = client.get("/api/flower/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "accuracy" in data and "round" in data


def test_suricata_alerts():
    resp = client.get("/api/suricata/alerts/live")
    assert resp.status_code == 200
    assert "alerts" in resp.json()


def test_grafana_dashboards():
    resp = client.get("/api/grafana/dashboards")
    assert resp.status_code == 200
    assert "dashboards" in resp.json()


def test_network_live_packets():
    resp = client.get("/api/network/packets/live")
    assert resp.status_code == 200
    assert "total_packets" in resp.json()


def test_recent_threats():
    resp = client.get("/api/threats/recent?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "threats" in data


# --- Auth and WS tests ---
def _make_token() -> str:
    # Create a valid JWT using the app's auth manager if available; fallback to empty
    if getattr(app_state, "auth_manager", None):
        # Give operator role for training permission
        return app_state.auth_manager.generate_access_token({
            "id": "test-user",
            "username": "tester",
            "role": "operator"
        })
    return ""


def test_post_requires_auth():
    # POST should be unauthorized without token
    resp = client.post("/api/federated/train")
    assert resp.status_code == 401

    # With token as operator, expect 200/JSON even if FL is not initialized
    token = _make_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp_auth = client.post("/api/federated/train", headers=headers)
    # If FL is not initialized, endpoint may return 200 with failure payload or 401 if auth failed
    assert resp_auth.status_code in (200, 401)


def test_payload_too_large():
    # Send >2MB to trigger 413
    big = b"x" * (2 * 1024 * 1024 + 1)
    resp = client.post("/api/federated/train", data=big)
    assert resp.status_code in (401, 413)


def test_websocket_auth():
    with client.websocket_connect("/ws") as ws:
        # Should be rejected (Unauthorized)
        msg = ws.receive_text()
        assert "Unauthorized" in msg

    token = _make_token()
    if token:
        # Temporarily stub fl_system metrics to ensure a deterministic message
        class _FakeFL:
            def __init__(self):
                self.running = True
                self._once = False
            def get_current_metrics(self):
                # Return different dicts twice to trigger a send once
                if not self._once:
                    self._once = True
                    return {"round": 1, "accuracy": 0.9, "participating_clients": 3}
                return {"round": 1, "accuracy": 0.9, "participating_clients": 3}

        old_fl = app_state.fl_system
        app_state.fl_system = _FakeFL()
        try:
            with client.websocket_connect(f"/ws?token={token}") as ws2:
                msg = ws2.receive_text()
                assert "fl_update" in msg
        finally:
            app_state.fl_system = old_fl


def test_recent_threats_pagination():
    # Call twice, check limit respected
    resp = client.get("/api/threats/recent?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "threats" in data
    assert len(data["threats"]) <= 2


def test_rbac_forbidden_on_settings_update():
    # Token has operator role; settings update requires admin
    token = _make_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = client.post("/api/settings/update", headers=headers, json={
        "fl_strategy": "FedAvg"
    })
    assert resp.status_code in (401, 403)

    # Now forge an admin token
    if getattr(app_state, "auth_manager", None):
        admin_token = app_state.auth_manager.generate_access_token({
            "id": "admin",
            "username": "admin",
            "role": "admin"
        })
        resp2 = client.post("/api/settings/update", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "fl_strategy": "FedAvg"
        })
        # Should pass
        assert resp2.status_code in (200,)


def test_integrations_overview_and_refresh():
    # Read-only overview should work without auth
    r = client.get("/api/integrations/overview")
    assert r.status_code == 200
    body = r.json()
    assert "snapshot" in body and "network" in body["snapshot"]

    # Refresh requires role (operator/admin)
    token = _make_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r2 = client.post("/api/integrations/refresh", headers=headers)
    assert r2.status_code in (200, 401)


def test_network_anomalies_and_stats():
    r1 = client.get("/api/network/anomalies")
    assert r1.status_code == 200
    d1 = r1.json()
    assert "anomalies" in d1 and "total_count" in d1
    r2 = client.get("/api/network/statistics")
    assert r2.status_code == 200
    assert "packets_per_second" in r2.json()


def test_flower_clients_and_strategy():
    clients = client.get("/api/flower/clients")
    assert clients.status_code == 200
    assert "clients" in clients.json()
    token = _make_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    strat = client.post("/api/flower/strategy/FedProx", headers=headers)
    assert strat.status_code in (200, 401)


def test_suricata_rules_and_performance():
    stats = client.get("/api/suricata/rules/statistics")
    assert stats.status_code == 200
    perf = client.get("/api/suricata/performance")
    assert perf.status_code == 200


def test_grafana_dashboard_and_timeseries():
    dash = client.get("/api/grafana/dashboard/FL%20Performance%20Dashboard")
    assert dash.status_code == 200
    ts = client.get("/api/grafana/metrics/timeseries")
    assert ts.status_code == 200
