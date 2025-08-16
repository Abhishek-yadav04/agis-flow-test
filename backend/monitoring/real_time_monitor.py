#!/usr/bin/env python3
"""
Real-time System Monitor - Updates every 500ms
"""

import threading
import time
import psutil
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RealTimeMonitor:
    """Ultra-fast real-time system monitoring"""
    
    def __init__(self):
        self.current_metrics = {}
        self.metrics_history = {"cpu": [], "memory": [], "disk": [], "network": []}
        self.is_monitoring = False
        self.update_interval = 0.5  # 500ms updates
        
    def start_monitoring(self):
        """Start ultra-fast monitoring"""
        self.is_monitoring = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        logger.info("Real-time monitoring started (500ms intervals)")
    
    def _monitoring_loop(self):
        """Main monitoring loop - updates every 500ms"""
        while self.is_monitoring:
            try:
                timestamp = time.time()
                
                # Get real-time metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk_usage = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Update current metrics
                self.current_metrics = {
                    "timestamp": timestamp,
                    "cpu": {
                        "percent": round(cpu_percent, 1),
                        "per_core": [round(c, 1) for c in psutil.cpu_percent(percpu=True)],
                        "count": psutil.cpu_count()
                    },
                    "memory": {
                        "percent": round(memory.percent, 1),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_gb": round(memory.used / (1024**3), 2),
                        "total_gb": round(memory.total / (1024**3), 2)
                    },
                    "disk": {
                        "percent": round((disk_usage.used / disk_usage.total) * 100, 1),
                        "free_gb": round(disk_usage.free / (1024**3), 2),
                        "used_gb": round(disk_usage.used / (1024**3), 2),
                        "total_gb": round(disk_usage.total / (1024**3), 2)
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    },
                    "processes": len(psutil.pids())
                }
                
                # Add to history (keep last 100 points)
                for metric in ["cpu", "memory", "disk"]:
                    self.metrics_history[metric].append({
                        "timestamp": timestamp,
                        "value": self.current_metrics[metric]["percent"]
                    })
                    if len(self.metrics_history[metric]) > 100:
                        self.metrics_history[metric] = self.metrics_history[metric][-100:]
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(1)
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics"""
        return self.current_metrics.copy()
    
    def get_metrics_history(self) -> Dict:
        """Get metrics history"""
        return self.metrics_history.copy()

# Global instance
real_time_monitor = RealTimeMonitor()

def initialize_monitoring():
    """Initialize real-time monitoring"""
    real_time_monitor.start_monitoring()

def get_monitoring_dashboard_data() -> Dict:
    """Get monitoring dashboard data"""
    return {
        "current_metrics": real_time_monitor.get_current_metrics(),
        "metrics_history": real_time_monitor.get_metrics_history()
    }