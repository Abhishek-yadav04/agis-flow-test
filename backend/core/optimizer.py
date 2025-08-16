"""
Advanced System Optimizer
Real-time performance optimization and resource management
"""

import asyncio
import psutil
import gc
import threading
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class SystemOptimizer:
    """Advanced system optimizer for production performance"""
    
    def __init__(self):
        self.is_running = False
        self.optimization_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.optimization_thread = None
        self.last_optimization = None
        
        # Optimization thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        
        # Performance targets
        self.target_response_time = 100  # ms
        self.target_throughput = 1000    # requests/sec
        
    def start_optimizer(self):
        """Start the optimization engine"""
        if self.is_running:
            return
            
        self.is_running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("System optimizer started")
        
    def stop_optimizer(self):
        """Stop the optimization engine"""
        self.is_running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("System optimizer stopped")
        
    def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_running:
            try:
                # Collect system metrics
                metrics = self._collect_metrics()
                
                # Analyze performance
                analysis = self._analyze_performance(metrics)
                
                # Apply optimizations
                optimizations = self._apply_optimizations(analysis)
                
                # Record optimization
                self._record_optimization(metrics, analysis, optimizations)
                
                # Sleep before next optimization cycle
                time.sleep(30)  # Optimize every 30 seconds
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                time.sleep(60)  # Wait longer on error
                
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1.0)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 1.0 or proc_info['memory_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            return {}
            
    def _analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system performance and identify bottlenecks"""
        analysis = {
            'issues': [],
            'recommendations': [],
            'severity': 'normal',
            'optimization_needed': False
        }
        
        if not metrics:
            return analysis
            
        # CPU analysis
        cpu_percent = metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.cpu_threshold:
            analysis['issues'].append(f"High CPU usage: {cpu_percent:.1f}%")
            analysis['recommendations'].append("Consider process optimization or scaling")
            analysis['optimization_needed'] = True
            analysis['severity'] = 'high' if cpu_percent > 90 else 'medium'
            
        # Memory analysis
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        if memory_percent > self.memory_threshold:
            analysis['issues'].append(f"High memory usage: {memory_percent:.1f}%")
            analysis['recommendations'].append("Trigger garbage collection and memory cleanup")
            analysis['optimization_needed'] = True
            analysis['severity'] = 'high' if memory_percent > 95 else 'medium'
            
        # Disk analysis
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        if disk_percent > self.disk_threshold:
            analysis['issues'].append(f"High disk usage: {disk_percent:.1f}%")
            analysis['recommendations'].append("Clean temporary files and logs")
            analysis['optimization_needed'] = True
            analysis['severity'] = 'critical' if disk_percent > 95 else 'high'
            
        # Process analysis
        processes = metrics.get('processes', [])
        high_cpu_processes = [p for p in processes if p['cpu_percent'] > 10]
        if high_cpu_processes:
            analysis['issues'].append(f"{len(high_cpu_processes)} processes using high CPU")
            analysis['recommendations'].append("Consider process optimization")
            
        return analysis
        
    def _apply_optimizations(self, analysis: Dict[str, Any]) -> List[str]:
        """Apply performance optimizations based on analysis"""
        optimizations_applied = []
        
        if not analysis.get('optimization_needed'):
            return optimizations_applied
            
        try:
            # Memory optimization
            if any('memory' in issue.lower() for issue in analysis.get('issues', [])):
                # Force garbage collection
                collected = gc.collect()
                if collected > 0:
                    optimizations_applied.append(f"Garbage collection freed {collected} objects")
                    
                # Clear caches (if any)
                self._clear_caches()
                optimizations_applied.append("System caches cleared")
                
            # CPU optimization
            if any('cpu' in issue.lower() for issue in analysis.get('issues', [])):
                # Adjust process priorities (if possible)
                self._optimize_process_priorities()
                optimizations_applied.append("Process priorities optimized")
                
            # Disk optimization
            if any('disk' in issue.lower() for issue in analysis.get('issues', [])):
                # Clean temporary files
                cleaned_size = self._clean_temp_files()
                if cleaned_size > 0:
                    optimizations_applied.append(f"Cleaned {cleaned_size:.1f}MB temporary files")
                    
        except Exception as e:
            logger.error(f"Optimization application error: {e}")
            optimizations_applied.append(f"Optimization error: {str(e)}")
            
        return optimizations_applied
        
    def _clear_caches(self):
        """Clear system caches"""
        try:
            # Clear Python caches
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
                
            # Clear import caches
            import importlib
            importlib.invalidate_caches()
            
        except Exception as e:
            logger.debug(f"Cache clearing error: {e}")
            
    def _optimize_process_priorities(self):
        """Optimize process priorities"""
        try:
            current_process = psutil.Process()
            # Set current process to high priority
            if hasattr(psutil, 'HIGH_PRIORITY_CLASS'):
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                current_process.nice(-5)  # Unix nice value
                
        except Exception as e:
            logger.debug(f"Process priority optimization error: {e}")
            
    def _clean_temp_files(self) -> float:
        """Clean temporary files and return size cleaned in MB"""
        try:
            import tempfile
            import shutil
            import os
            
            temp_dir = tempfile.gettempdir()
            total_size = 0
            
            # Clean Python cache files
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.pyo'):
                        try:
                            file_path = os.path.join(root, file)
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_size += size
                        except Exception:
                            continue
                            
                # Remove __pycache__ directories
                if '__pycache__' in dirs:
                    try:
                        cache_path = os.path.join(root, '__pycache__')
                        shutil.rmtree(cache_path)
                    except Exception:
                        continue
                        
            return total_size / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            logger.debug(f"Temp file cleaning error: {e}")
            return 0.0
            
    def _record_optimization(self, metrics: Dict[str, Any], analysis: Dict[str, Any], optimizations: List[str]):
        """Record optimization results"""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': metrics,
            'analysis': analysis,
            'optimizations': optimizations,
            'performance_impact': self._calculate_performance_impact()
        }
        
        self.optimization_history.append(record)
        self.last_optimization = record
        
        # Log significant optimizations
        if optimizations:
            logger.info(f"Applied {len(optimizations)} optimizations: {', '.join(optimizations)}")
            
    def _calculate_performance_impact(self) -> Dict[str, float]:
        """Calculate performance impact of optimizations"""
        if len(self.optimization_history) < 2:
            return {}
            
        try:
            current = self.optimization_history[-1]['metrics']
            previous = self.optimization_history[-2]['metrics']
            
            cpu_change = current.get('cpu', {}).get('percent', 0) - previous.get('cpu', {}).get('percent', 0)
            memory_change = current.get('memory', {}).get('percent', 0) - previous.get('memory', {}).get('percent', 0)
            
            return {
                'cpu_change': cpu_change,
                'memory_change': memory_change,
                'improvement_score': max(0, -(cpu_change + memory_change) / 2)
            }
            
        except Exception as e:
            logger.debug(f"Performance impact calculation error: {e}")
            return {}
            
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'is_running': self.is_running,
            'last_optimization': self.last_optimization,
            'optimization_count': len(self.optimization_history),
            'average_improvement': self._calculate_average_improvement(),
            'current_thresholds': {
                'cpu': self.cpu_threshold,
                'memory': self.memory_threshold,
                'disk': self.disk_threshold
            }
        }
        
    def _calculate_average_improvement(self) -> float:
        """Calculate average performance improvement"""
        if len(self.optimization_history) < 10:
            return 0.0
            
        try:
            improvements = []
            for record in list(self.optimization_history)[-10:]:
                impact = record.get('performance_impact', {})
                improvement = impact.get('improvement_score', 0)
                if improvement > 0:
                    improvements.append(improvement)
                    
            return np.mean(improvements) if improvements else 0.0
            
        except Exception as e:
            logger.debug(f"Average improvement calculation error: {e}")
            return 0.0
            
    def force_optimization(self) -> Dict[str, Any]:
        """Force immediate optimization"""
        try:
            metrics = self._collect_metrics()
            analysis = self._analyze_performance(metrics)
            optimizations = self._apply_optimizations(analysis)
            self._record_optimization(metrics, analysis, optimizations)
            
            return {
                'success': True,
                'optimizations_applied': len(optimizations),
                'details': optimizations,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Force optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global optimizer instance
system_optimizer = SystemOptimizer()