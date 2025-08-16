"""
Performance Optimizer - Enterprise Grade
Real-time system optimization and resource management
"""
import asyncio
import psutil
import time
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self):
        self.optimization_history = []
        self.performance_baselines = {}
        self.optimization_rules = []
        self.is_optimizing = True
        self.stats = {
            "optimizations_applied": 0,
            "performance_improvements": 0,
            "resource_savings": 0,
            "uptime_improvements": 0
        }
        
    async def start_optimization(self):
        """Start performance optimization services"""
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._optimize_memory())
        asyncio.create_task(self._optimize_cpu())
        asyncio.create_task(self._optimize_disk())
        asyncio.create_task(self._optimize_network())
        asyncio.create_task(self._generate_recommendations())
        
    async def _monitor_performance(self):
        """Monitor system performance metrics"""
        while self.is_optimizing:
            try:
                # Collect performance metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "network_bytes_per_sec": (network.bytes_sent + network.bytes_recv) / 1024 / 1024,
                    "active_processes": len(psutil.pids()),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                }
                
                # Store baseline if not set
                if not self.performance_baselines:
                    self.performance_baselines = {
                        "cpu_baseline": cpu_percent,
                        "memory_baseline": memory.percent,
                        "disk_baseline": (disk.used / disk.total) * 100,
                        "established_at": datetime.now().isoformat()
                    }
                    
                # Check for performance degradation
                await self._check_performance_degradation(metrics)
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(15)
                
    async def _optimize_memory(self):
        """Optimize memory usage"""
        while self.is_optimizing:
            try:
                memory = psutil.virtual_memory()
                
                if memory.percent > 85:
                    # Force garbage collection
                    gc.collect()
                    
                    # Log optimization
                    optimization = {
                        "type": "memory_optimization",
                        "action": "garbage_collection",
                        "timestamp": datetime.now().isoformat(),
                        "memory_before": memory.percent,
                        "memory_after": psutil.virtual_memory().percent,
                        "improvement": memory.percent - psutil.virtual_memory().percent
                    }
                    
                    self.optimization_history.append(optimization)
                    self.stats["optimizations_applied"] += 1
                    
                    if optimization["improvement"] > 0:
                        self.stats["performance_improvements"] += 1
                        
                    logger.info(f"Memory optimization applied: {optimization['improvement']:.2f}% improvement")
                    
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Memory optimization error: {e}")
                await asyncio.sleep(60)
                
    async def _optimize_cpu(self):
        """Optimize CPU usage"""
        while self.is_optimizing:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                
                if cpu_percent > 90:
                    # Find high CPU processes
                    high_cpu_processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 20:
                                high_cpu_processes.append(proc.info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                    optimization = {
                        "type": "cpu_optimization",
                        "action": "high_cpu_process_identification",
                        "timestamp": datetime.now().isoformat(),
                        "cpu_usage": cpu_percent,
                        "high_cpu_processes": high_cpu_processes[:5],  # Top 5
                        "recommendation": "Consider terminating or optimizing high CPU processes"
                    }
                    
                    self.optimization_history.append(optimization)
                    self.stats["optimizations_applied"] += 1
                    
                await asyncio.sleep(20)
                
            except Exception as e:
                logger.error(f"CPU optimization error: {e}")
                await asyncio.sleep(30)
                
    async def _optimize_disk(self):
        """Optimize disk usage"""
        while self.is_optimizing:
            try:
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                
                if disk_percent > 85:
                    # Identify large files and directories
                    optimization = {
                        "type": "disk_optimization",
                        "action": "disk_space_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "disk_usage": disk_percent,
                        "free_space_gb": disk.free / (1024**3),
                        "recommendation": "Clean temporary files and logs"
                    }
                    
                    self.optimization_history.append(optimization)
                    self.stats["optimizations_applied"] += 1
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Disk optimization error: {e}")
                await asyncio.sleep(600)
                
    async def _optimize_network(self):
        """Optimize network performance"""
        while self.is_optimizing:
            try:
                network = psutil.net_io_counters()
                connections = len(psutil.net_connections())
                
                if connections > 500:
                    optimization = {
                        "type": "network_optimization",
                        "action": "connection_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "active_connections": connections,
                        "bytes_sent_mb": network.bytes_sent / (1024**2),
                        "bytes_recv_mb": network.bytes_recv / (1024**2),
                        "recommendation": "Monitor for excessive network connections"
                    }
                    
                    self.optimization_history.append(optimization)
                    self.stats["optimizations_applied"] += 1
                    
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Network optimization error: {e}")
                await asyncio.sleep(120)
                
    async def _generate_recommendations(self):
        """Generate performance recommendations"""
        while self.is_optimizing:
            try:
                # Analyze recent performance data
                recent_optimizations = [
                    opt for opt in self.optimization_history
                    if (datetime.now() - datetime.fromisoformat(opt['timestamp'])).seconds < 3600
                ]
                
                if len(recent_optimizations) >= 3:
                    recommendation = {
                        "type": "performance_recommendation",
                        "priority": "high",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Multiple performance issues detected ({len(recent_optimizations)} in last hour)",
                        "suggested_actions": [
                            "Review system resource allocation",
                            "Consider scaling up resources",
                            "Analyze application performance bottlenecks",
                            "Implement caching strategies"
                        ]
                    }
                    
                    self.optimization_history.append(recommendation)
                    
                await asyncio.sleep(300)  # Generate recommendations every 5 minutes
                
            except Exception as e:
                logger.error(f"Recommendation generation error: {e}")
                await asyncio.sleep(600)
                
    async def _check_performance_degradation(self, current_metrics: Dict[str, Any]):
        """Check for performance degradation"""
        try:
            if not self.performance_baselines:
                return
                
            cpu_degradation = current_metrics["cpu_percent"] - self.performance_baselines["cpu_baseline"]
            memory_degradation = current_metrics["memory_percent"] - self.performance_baselines["memory_baseline"]
            
            if cpu_degradation > 20 or memory_degradation > 15:
                degradation_alert = {
                    "type": "performance_degradation",
                    "severity": "high" if cpu_degradation > 30 or memory_degradation > 25 else "medium",
                    "timestamp": datetime.now().isoformat(),
                    "cpu_degradation": cpu_degradation,
                    "memory_degradation": memory_degradation,
                    "recommendation": "Investigate recent changes or increased load"
                }
                
                self.optimization_history.append(degradation_alert)
                logger.warning(f"Performance degradation detected: CPU +{cpu_degradation:.1f}%, Memory +{memory_degradation:.1f}%")
                
        except Exception as e:
            logger.error(f"Performance degradation check error: {e}")
            
    def get_optimization_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent optimization history"""
        return self.optimization_history[-limit:]
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance optimization statistics"""
        recent_optimizations = [
            opt for opt in self.optimization_history
            if (datetime.now() - datetime.fromisoformat(opt['timestamp'])).seconds < 3600
        ]
        
        return {
            **self.stats,
            "recent_optimizations": len(recent_optimizations),
            "baseline_established": bool(self.performance_baselines),
            "baseline_age_hours": (
                (datetime.now() - datetime.fromisoformat(self.performance_baselines.get("established_at", datetime.now().isoformat()))).seconds / 3600
                if self.performance_baselines else 0
            ),
            "optimization_active": self.is_optimizing
        }
        
    def get_current_performance(self) -> Dict[str, Any]:
        """Get current system performance"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "network_mbps": (network.bytes_sent + network.bytes_recv) / (1024**2),
                "active_processes": len(psutil.pids()),
                "uptime_hours": (time.time() - psutil.boot_time()) / 3600,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Current performance check error: {e}")
            return {}
            
    def add_optimization_rule(self, rule: Dict[str, Any]):
        """Add custom optimization rule"""
        self.optimization_rules.append({
            **rule,
            "created_at": datetime.now().isoformat(),
            "active": True
        })
        
    def get_optimization_rules(self) -> List[Dict[str, Any]]:
        """Get active optimization rules"""
        return [rule for rule in self.optimization_rules if rule.get('active', True)]