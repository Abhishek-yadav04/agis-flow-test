"""
Production-Grade Metrics and Monitoring
Comprehensive system monitoring with alerts
"""

import time
import threading
import psutil
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import json

logger = logging.getLogger(__name__)

class ProductionMetrics:
    """Production-grade metrics collection and monitoring"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # Last 1000 data points
        self.alerts = deque(maxlen=100)  # Last 100 alerts
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Thresholds for alerting
        self.thresholds = {
            "cpu_critical": 90.0,
            "cpu_warning": 75.0,
            "memory_critical": 90.0,
            "memory_warning": 80.0,
            "disk_critical": 95.0,
            "disk_warning": 85.0,
            "response_time_critical": 5000,  # ms
            "response_time_warning": 2000,   # ms
            "error_rate_critical": 5.0,     # %
            "error_rate_warning": 2.0       # %
        }
        
        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
        self.endpoint_stats = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0})
        
    def start_monitoring(self):
        """Start production monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Production monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                time.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Application metrics
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            metrics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system": {
                    "cpu": {
                        "percent": round(cpu_percent, 2),
                        "count": cpu_count,
                        "frequency_mhz": cpu_freq.current if cpu_freq else 0
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_gb": round(memory.used / (1024**3), 2),
                        "percent": round(memory.percent, 2),
                        "swap_percent": round(swap.percent, 2)
                    },
                    "disk": {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "used_gb": round(disk.used / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2),
                        "percent": round((disk.used / disk.total) * 100, 2),
                        "read_mb": round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                        "write_mb": round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
                    },
                    "network": {
                        "bytes_sent_mb": round(network.bytes_sent / (1024**2), 2),
                        "bytes_recv_mb": round(network.bytes_recv / (1024**2), 2),
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv,
                        "errors_in": network.errin,
                        "errors_out": network.errout
                    },
                    "processes": process_count
                },
                "application": {
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate_percent": round(error_rate, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "active_endpoints": len(self.endpoint_stats)
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        try:
            system = metrics.get("system", {})
            app = metrics.get("application", {})
            
            # CPU alerts
            cpu_percent = system.get("cpu", {}).get("percent", 0)
            if cpu_percent >= self.thresholds["cpu_critical"]:
                self._create_alert("CRITICAL", "CPU", f"CPU usage at {cpu_percent}%", metrics["timestamp"])
            elif cpu_percent >= self.thresholds["cpu_warning"]:
                self._create_alert("WARNING", "CPU", f"CPU usage at {cpu_percent}%", metrics["timestamp"])
            
            # Memory alerts
            memory_percent = system.get("memory", {}).get("percent", 0)
            if memory_percent >= self.thresholds["memory_critical"]:
                self._create_alert("CRITICAL", "MEMORY", f"Memory usage at {memory_percent}%", metrics["timestamp"])
            elif memory_percent >= self.thresholds["memory_warning"]:
                self._create_alert("WARNING", "MEMORY", f"Memory usage at {memory_percent}%", metrics["timestamp"])
            
            # Disk alerts
            disk_percent = system.get("disk", {}).get("percent", 0)
            if disk_percent >= self.thresholds["disk_critical"]:
                self._create_alert("CRITICAL", "DISK", f"Disk usage at {disk_percent}%", metrics["timestamp"])
            elif disk_percent >= self.thresholds["disk_warning"]:
                self._create_alert("WARNING", "DISK", f"Disk usage at {disk_percent}%", metrics["timestamp"])
            
            # Application alerts
            error_rate = app.get("error_rate_percent", 0)
            if error_rate >= self.thresholds["error_rate_critical"]:
                self._create_alert("CRITICAL", "APPLICATION", f"Error rate at {error_rate}%", metrics["timestamp"])
            elif error_rate >= self.thresholds["error_rate_warning"]:
                self._create_alert("WARNING", "APPLICATION", f"Error rate at {error_rate}%", metrics["timestamp"])
            
            avg_response_time = app.get("avg_response_time_ms", 0)
            if avg_response_time >= self.thresholds["response_time_critical"]:
                self._create_alert("CRITICAL", "PERFORMANCE", f"Response time at {avg_response_time}ms", metrics["timestamp"])
            elif avg_response_time >= self.thresholds["response_time_warning"]:
                self._create_alert("WARNING", "PERFORMANCE", f"Response time at {avg_response_time}ms", metrics["timestamp"])
                
        except Exception as e:
            logger.error(f"Alert checking error: {e}")
    
    def _create_alert(self, severity: str, category: str, message: str, timestamp: str):
        """Create and store alert"""
        alert = {
            "id": f"alert_{int(time.time())}_{len(self.alerts)}",
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": timestamp,
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{severity}] {category}: {message}")
    
    def record_request(self, endpoint: str, response_time_ms: float, status_code: int):
        """Record request metrics"""
        self.request_count += 1
        self.response_times.append(response_time_ms)
        
        # Update endpoint stats
        self.endpoint_stats[endpoint]["count"] += 1
        self.endpoint_stats[endpoint]["total_time"] += response_time_ms
        
        if status_code >= 400:
            self.error_count += 1
            self.endpoint_stats[endpoint]["errors"] += 1
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_system_metrics()
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for specified minutes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        filtered_metrics = []
        for metric in self.metrics_history:
            try:
                metric_time = datetime.fromisoformat(metric["timestamp"].replace('Z', '+00:00'))
                if metric_time >= cutoff_time:
                    filtered_metrics.append(metric)
            except:
                continue
                
        return filtered_metrics
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        alerts = list(self.alerts)
        
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False
    
    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """Get endpoint performance statistics"""
        stats = {}
        for endpoint, data in self.endpoint_stats.items():
            avg_response_time = data["total_time"] / max(data["count"], 1)
            error_rate = (data["errors"] / max(data["count"], 1)) * 100
            
            stats[endpoint] = {
                "request_count": data["count"],
                "error_count": data["errors"],
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2)
            }
        
        return stats
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        current_metrics = self.get_current_metrics()
        recent_alerts = self.get_alerts(limit=10)
        critical_alerts = [alert for alert in recent_alerts if alert["severity"] == "CRITICAL"]
        
        # Calculate health score (0-100)
        health_score = 100
        
        if current_metrics.get("system"):
            system = current_metrics["system"]
            
            # Deduct points for high resource usage
            cpu_percent = system.get("cpu", {}).get("percent", 0)
            memory_percent = system.get("memory", {}).get("percent", 0)
            disk_percent = system.get("disk", {}).get("percent", 0)
            
            if cpu_percent > 80:
                health_score -= (cpu_percent - 80) * 2
            if memory_percent > 80:
                health_score -= (memory_percent - 80) * 2
            if disk_percent > 80:
                health_score -= (disk_percent - 80) * 2
        
        # Deduct points for errors and alerts
        if current_metrics.get("application"):
            error_rate = current_metrics["application"].get("error_rate_percent", 0)
            health_score -= error_rate * 5
        
        health_score -= len(critical_alerts) * 10
        health_score = max(0, min(100, health_score))
        
        return {
            "health_score": round(health_score, 1),
            "status": "HEALTHY" if health_score >= 80 else "DEGRADED" if health_score >= 60 else "UNHEALTHY",
            "critical_alerts": len(critical_alerts),
            "total_alerts": len(recent_alerts),
            "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 1),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

# Global metrics instance
production_metrics = ProductionMetrics()