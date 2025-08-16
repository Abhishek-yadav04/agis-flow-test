"""
WebSocket Connection Manager - Core Module
Professional WebSocket connection management with real-time features
"""
import asyncio
import json
import time
from typing import Set, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import logging
try:
    from logging.structured import log_event  # type: ignore
except Exception:
    def log_event(level: str, event: str, **fields):
        getattr(logging, level if level in ("info","warning","error","debug") else "info")(f"{event} | {fields}")

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        """Initialize connection manager state."""
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.message_queue: Dict[WebSocket, list] = {}
        self._failure_counts: Dict[WebSocket, int] = {}
        self._max_queue = 100  # backpressure cap threshold
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
        }
        self.heartbeat_interval = 30  # seconds
        self.inactivity_timeout = 300  # seconds

    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept and register a new WebSocket connection with metadata and structured log."""
        await websocket.accept()
        self.active_connections.add(websocket)

        safe_client_info = self._sanitize_client_info(client_info or {})
        client_ip = self._sanitize_ip(websocket.client.host if websocket.client else "unknown")
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(timezone.utc),
            "client_ip": client_ip,
            "user_agent": safe_client_info.get("user_agent", "unknown"),
            "last_activity": datetime.now(timezone.utc),
            "messages_sent": 0,
            "messages_received": 0
        }

        self.message_queue[websocket] = []
        self._failure_counts[websocket] = 0
        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.active_connections)

        logger.info(f"WebSocket connected: {client_ip}")
        log_event("info", "ws_connected", client_ip=client_ip, total=len(self.active_connections))

    def _sanitize_client_info(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in client_info.items():
            if isinstance(value, str):
                sanitized[key] = value.replace('\n', '\\n').replace('\r', '\\r')
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_ip(self, ip: str) -> str:
        return ip.replace('\n', '\\n').replace('\r', '\\r') if isinstance(ip, str) else "unknown"

    def disconnect(self, websocket: WebSocket):
        """Disconnect and cleanup a WebSocket connection with structured log."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        if websocket in self.message_queue:
            del self.message_queue[websocket]
        if websocket in self._failure_counts:
            del self._failure_counts[websocket]
        self.stats["active_connections"] = len(self.active_connections)
        logger.info("WebSocket disconnected")
        log_event("info", "ws_disconnected", remaining=len(self.active_connections))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            self.stats["messages_sent"] += 1
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["messages_sent"] += 1
                self.connection_metadata[websocket]["last_activity"] = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str, exclude: Set[WebSocket] = None):
        if not self.active_connections:
            return
        exclude = exclude or set()
        disconnected = set()
        for connection in list(self.active_connections):
            if connection in exclude:
                continue
            try:
                # Enforce backpressure: accumulate unsent messages? Here we just drop if queue exceed
                q_meta = self.connection_metadata.get(connection)
                if q_meta:
                    # lazy queue tracking via messages_sent - if too many since last activity drop
                    if q_meta.get("messages_sent", 0) - q_meta.get("messages_received", 0) > self._max_queue:
                        log_event("warning", "ws_backpressure_disconnect")
                        disconnected.add(connection)
                        continue
                await connection.send_text(message)
                self.stats["messages_sent"] += 1
                if connection in self.connection_metadata:
                    meta = self.connection_metadata[connection]
                    meta["messages_sent"] += 1
                    meta["last_activity"] = datetime.now(timezone.utc)
                # success resets failure counter
                if connection in self._failure_counts:
                    self._failure_counts[connection] = 0
            except Exception as e:
                self._failure_counts[connection] = self._failure_counts.get(connection, 0) + 1
                fail_count = self._failure_counts[connection]
                if fail_count <= 3:
                    logger.warning(f"Broadcast failure {fail_count}: {e}")
                    log_event("warning", "ws_broadcast_failure", failure=str(e), count=fail_count)
                elif fail_count == 4:
                    logger.warning("Suppressing further broadcast errors for this connection")
                    log_event("warning", "ws_broadcast_suppressed")
                if fail_count >= 4:
                    disconnected.add(connection)
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_json(self, data: Dict[str, Any], exclude: Set[WebSocket] = None):
        await self.broadcast(json.dumps(data), exclude)

    async def send_json(self, data: Dict[str, Any], websocket: WebSocket):
        await self.send_personal_message(json.dumps(data), websocket)

    def get_connection_count(self) -> int:
        return len(self.active_connections)

    def get_connection_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "connection_details": [
                {
                    "client_ip": meta.get("client_ip"),
                    "connected_at": meta.get("connected_at").isoformat() if meta.get("connected_at") else None,
                    "last_activity": meta.get("last_activity").isoformat() if meta.get("last_activity") else None,
                    "messages_sent": meta.get("messages_sent", 0),
                    "messages_received": meta.get("messages_received", 0)
                }
                for meta in self.connection_metadata.values()
            ]
        }

    async def handle_message(self, websocket: WebSocket, message: str):
        try:
            self.stats["messages_received"] += 1
            if websocket in self.connection_metadata:
                meta = self.connection_metadata[websocket]
                meta["messages_received"] += 1
                meta["last_activity"] = datetime.now(timezone.utc)
            try:
                data = json.loads(message)
                await self._process_message(websocket, data)
            except json.JSONDecodeError:
                await self.send_json({"error": "Invalid JSON format"}, websocket)
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _process_message(self, websocket: WebSocket, data: Dict[str, Any]):
        message_type = data.get("type")
        if message_type == "ping":
            await self.send_json({"type": "pong", "timestamp": time.time()}, websocket)
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["last_activity"] = datetime.now(timezone.utc)
        elif message_type == "subscribe":
            await self.send_json({"type": "subscribed", "channel": data.get("channel")}, websocket)
        else:
            await self.send_json({"type": "echo", "data": data}, websocket)

    async def cleanup_inactive_connections(self, timeout_seconds: int = 300):
        current_time = datetime.now(timezone.utc)
        inactive = []
        for ws, metadata in self.connection_metadata.items():
            last_activity = metadata.get("last_activity")
            if last_activity and (current_time - last_activity).seconds > timeout_seconds:
                inactive.append(ws)
        for ws in inactive:
            try:
                await ws.close()
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.debug(f"Error closing inactive websocket: {e}", exc_info=True)
            self.disconnect(ws)
        if inactive:
            logger.info(f"Cleaned up {len(inactive)} inactive connections")

    async def send_heartbeat(self):
        if not self.active_connections:
            return
        to_close = []
        for ws in list(self.active_connections):
            try:
                await ws.send_text(json.dumps({"type": "ping", "timestamp": time.time()}))
                # Inactivity check
                meta = self.connection_metadata.get(ws)
                if meta:
                    last = meta.get("last_activity")
                    if last and (datetime.now(timezone.utc) - last).total_seconds() > self.inactivity_timeout:
                        log_event("info", "ws_inactive_disconnect")
                        to_close.append(ws)
            except Exception:
                to_close.append(ws)
        for ws in to_close:
            try:
                await ws.close()
            except Exception:
                pass
            self.disconnect(ws)
        # prune failure counts for removed connections
        for ws in list(self._failure_counts.keys()):
            if ws not in self.active_connections:
                self._failure_counts.pop(ws, None)

# Global connection manager instance
connection_manager = ConnectionManager()