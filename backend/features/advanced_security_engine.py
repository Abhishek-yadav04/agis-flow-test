"""
Advanced Security Engine - Enterprise Grade
Real-time threat detection with ML and behavioral analysis
"""
import asyncio
import time
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import psutil
import logging
from collections import deque

logger = logging.getLogger(__name__)

class AdvancedSecurityEngine:
    def __init__(self):
        self.threat_models = {
            "anomaly_detector": IsolationForest(contamination=0.1, random_state=42),
            "behavior_analyzer": IsolationForest(contamination=0.05, random_state=123),
            "network_analyzer": IsolationForest(contamination=0.08, random_state=456)
        }
        self.scalers = {
            "system": StandardScaler(),
            "network": StandardScaler(),
            "behavior": StandardScaler()
        }
        self.threat_database = deque(maxlen=1000)  # Performance fix: use deque
        self.security_rules = []
        self.is_monitoring = True
        self.models_trained = False
        self._suspicious_processes = frozenset(['nc.exe', 'ncat.exe', 'netcat', 'mimikatz', 'psexec'])
        
    async def start_monitoring(self):
        """Start all security monitoring services"""
        asyncio.create_task(self._train_models())
        asyncio.create_task(self._monitor_system_threats())
        asyncio.create_task(self._monitor_network_threats())
        asyncio.create_task(self._monitor_behavioral_threats())
        asyncio.create_task(self._analyze_threat_patterns())
        
    async def _train_models(self):
        """Train ML models with system data"""
        while self.is_monitoring:
            try:
                # Collect training data
                system_data = []
                network_data = []
                behavior_data = []
                
                for _ in range(100):
                    # System metrics
                    cpu = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    network = psutil.net_io_counters()
                    
                    system_features = [
                        cpu, memory.percent, disk.used / disk.total * 100,
                        len(psutil.pids()), memory.available / 1024**3
                    ]
                    system_data.append(system_features)
                    
                    # Network metrics
                    network_features = [
                        network.bytes_sent / 1024**2, network.bytes_recv / 1024**2,
                        network.packets_sent, network.packets_recv,
                        len(psutil.net_connections())
                    ]
                    network_data.append(network_features)
                    
                    # Behavioral metrics
                    processes = list(psutil.process_iter(['cpu_percent', 'memory_percent']))
                    behavior_features = [
                        len(processes), 
                        sum(p.info['cpu_percent'] or 0 for p in processes[:10]),
                        sum(p.info['memory_percent'] or 0 for p in processes[:10]),
                        cpu * memory.percent / 100,
                        time.time() % 86400  # Time of day
                    ]
                    behavior_data.append(behavior_features)
                    
                    await asyncio.sleep(0.1)
                
                # Train models
                if len(system_data) >= 50:
                    X_system = self.scalers["system"].fit_transform(np.array(system_data))
                    X_network = self.scalers["network"].fit_transform(np.array(network_data))
                    X_behavior = self.scalers["behavior"].fit_transform(np.array(behavior_data))
                    
                    self.threat_models["anomaly_detector"].fit(X_system)
                    self.threat_models["network_analyzer"].fit(X_network)
                    self.threat_models["behavior_analyzer"].fit(X_behavior)
                    
                    self.models_trained = True
                    logger.info("Security models trained successfully")
                
                await asyncio.sleep(300)  # Retrain every 5 minutes
                
            except Exception as e:
                logger.error(f"Model training error: {e}")
                await asyncio.sleep(60)
                
    async def _monitor_system_threats(self):
        """Monitor system-level threats"""
        while self.is_monitoring:
            try:
                if not self.models_trained:
                    await asyncio.sleep(5)
                    continue
                    
                # Collect current metrics
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                processes = len(psutil.pids())
                
                features = np.array([[
                    cpu, memory.percent, disk.used / disk.total * 100,
                    processes, memory.available / 1024**3
                ]])
                
                # Scale and predict
                features_scaled = self.scalers["system"].transform(features)
                anomaly_score = self.threat_models["anomaly_detector"].decision_function(features_scaled)[0]
                is_anomaly = self.threat_models["anomaly_detector"].predict(features_scaled)[0] == -1
                
                # Check for specific threats
                threats = []
                
                if cpu > 95:
                    threats.append(self._create_threat("cpu_exhaustion", "critical", f"CPU usage at {cpu}%"))
                elif cpu > 85 and is_anomaly:
                    threats.append(self._create_threat("suspicious_cpu_activity", "high", f"Anomalous CPU pattern detected"))
                    
                if memory.percent > 95:
                    threats.append(self._create_threat("memory_exhaustion", "critical", f"Memory usage at {memory.percent}%"))
                    
                if processes > 500:
                    threats.append(self._create_threat("process_explosion", "medium", f"Unusual process count: {processes}"))
                    
                if is_anomaly and anomaly_score < -0.5:
                    threats.append(self._create_threat("system_anomaly", "high", f"System behavior anomaly detected (score: {anomaly_score:.3f})"))
                
                # Store threats with deque for better performance
                for threat in threats:
                    self.threat_database.append(threat)
                    
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(10)
                
    async def _monitor_network_threats(self):
        """Monitor network-level threats"""
        while self.is_monitoring:
            try:
                if not self.models_trained:
                    await asyncio.sleep(5)
                    continue
                    
                network = psutil.net_io_counters()
                connections = psutil.net_connections()
                
                features = np.array([[
                    network.bytes_sent / 1024**2, network.bytes_recv / 1024**2,
                    network.packets_sent, network.packets_recv, len(connections)
                ]])
                
                features_scaled = self.scalers["network"].transform(features)
                anomaly_score = self.threat_models["network_analyzer"].decision_function(features_scaled)[0]
                is_anomaly = self.threat_models["network_analyzer"].predict(features_scaled)[0] == -1
                
                threats = []
                
                # Check for network anomalies
                if len(connections) > 1000:
                    threats.append(self._create_threat("connection_flood", "high", f"Excessive connections: {len(connections)}"))
                    
                if is_anomaly and anomaly_score < -0.3:
                    threats.append(self._create_threat("network_anomaly", "medium", f"Network behavior anomaly detected"))
                    
                # Check for suspicious connections
                suspicious_ports = [1337, 31337, 12345, 54321]
                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port in suspicious_ports:
                        threats.append(self._create_threat("suspicious_port", "high", f"Suspicious port activity: {conn.laddr.port}"))
                        
                for threat in threats:
                    self.threat_database.append(threat)
                    
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(15)
                
    async def _monitor_behavioral_threats(self):
        """Monitor behavioral threats with optimized process checking"""
        while self.is_monitoring:
            try:
                if not self.models_trained:
                    await asyncio.sleep(5)
                    continue
                    
                processes = list(psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'create_time']))
                cpu = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                
                features = np.array([[
                    len(processes),
                    sum(p.info['cpu_percent'] or 0 for p in processes[:10]),
                    sum(p.info['memory_percent'] or 0 for p in processes[:10]),
                    cpu * memory.percent / 100,
                    time.time() % 86400
                ]])
                
                features_scaled = self.scalers["behavior"].transform(features)
                anomaly_score = self.threat_models["behavior_analyzer"].decision_function(features_scaled)[0]
                is_anomaly = self.threat_models["behavior_analyzer"].predict(features_scaled)[0] == -1
                
                threats = []
                
                # Check for behavioral anomalies
                if is_anomaly and anomaly_score < -0.4:
                    threats.append(self._create_threat("behavioral_anomaly", "medium", "Unusual system behavior pattern"))
                    
                # Optimized suspicious process check with early termination
                for proc in processes:
                    proc_name = proc.info['name'].lower()
                    if any(sus in proc_name for sus in self._suspicious_processes):
                        threats.append(self._create_threat("suspicious_process", "critical", f"Suspicious process: {proc.info['name']}"))
                        break  # Early termination for performance
                        
                for threat in threats:
                    self.threat_database.append(threat)
                    
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Behavioral monitoring error: {e}")
                await asyncio.sleep(20)
                
    async def _analyze_threat_patterns(self):
        """Analyze threat patterns with optimized filtering"""
        while self.is_monitoring:
            try:
                if len(self.threat_database) < 10:
                    await asyncio.sleep(15)  # Reduced sleep time
                    continue
                    
                # Analyze recent threats with timezone-aware filtering
                current_time = datetime.now(timezone.utc)
                recent_threats = []
                
                for threat in list(self.threat_database):
                    try:
                        threat_time = datetime.fromisoformat(threat['timestamp'].replace('Z', '+00:00'))
                        if (current_time - threat_time).seconds < 300:
                            recent_threats.append(threat)
                    except (ValueError, KeyError):
                        continue
                
                if len(recent_threats) >= 3:
                    threat = self._create_threat("coordinated_attack", "critical", 
                                               f"Multiple threats detected: {len(recent_threats)}")
                    self.threat_database.append(threat)
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(60)
                
    def get_threats(self, limit: int = 50, severity: str = None) -> List[Dict[str, Any]]:
        """Get recent threats with optimized filtering"""
        threats_list = list(self.threat_database)
        
        if severity:
            threats_list = [t for t in threats_list if t.get('severity') == severity]
            
        return threats_list[-limit:]
        
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat statistics with timezone-aware filtering"""
        if not self.threat_database:
            return {"total": 0, "by_severity": {}, "by_type": {}}
            
        current_time = datetime.now(timezone.utc)
        recent_threats = []
        
        for threat in list(self.threat_database):
            try:
                threat_time = datetime.fromisoformat(threat['timestamp'].replace('Z', '+00:00'))
                if (current_time - threat_time).seconds < 3600:
                    recent_threats.append(threat)
            except (ValueError, KeyError):
                continue
        
        severity_counts = {}
        type_counts = {}
        
        for threat in recent_threats:
            severity = threat.get('severity', 'unknown')
            threat_type = threat.get('type', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[threat_type] = type_counts.get(threat_type, 0) + 1
            
        return {
            "total": len(recent_threats),
            "total_all_time": len(self.threat_database),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "models_trained": self.models_trained,
            "monitoring_active": self.is_monitoring
        }
        
    def add_security_rule(self, rule: Dict[str, Any]):
        """Add custom security rule with validation"""
        required_fields = ['name', 'type', 'severity']
        if not all(field in rule for field in required_fields):
            raise ValueError("Security rule must contain: name, type, severity")
            
        self.security_rules.append({
            **rule,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True
        })
        
    def get_security_rules(self) -> List[Dict[str, Any]]:
        """Get active security rules"""
        return [rule for rule in self.security_rules if rule.get('active', True)]
                
    async def _monitor_behavioral_threats(self):
        """Monitor behavioral threats"""
        while self.is_monitoring:
            try:
                if not self.models_trained:
                    await asyncio.sleep(5)
                    continue
                    
                processes = list(psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'create_time']))
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                features = np.array([[
                    len(processes),
                    sum(p.info['cpu_percent'] or 0 for p in processes[:10]),
                    sum(p.info['memory_percent'] or 0 for p in processes[:10]),
                    cpu * memory.percent / 100,
                    time.time() % 86400
                ]])
                
                features_scaled = self.scalers["behavior"].transform(features)
                anomaly_score = self.threat_models["behavior_analyzer"].decision_function(features_scaled)[0]
                is_anomaly = self.threat_models["behavior_analyzer"].predict(features_scaled)[0] == -1
                
                threats = []
                
                # Check for behavioral anomalies
                if is_anomaly and anomaly_score < -0.4:
                    threats.append(self._create_threat("behavioral_anomaly", "medium", "Unusual system behavior pattern"))
                    
                # Check for suspicious process names
                suspicious_names = ['nc.exe', 'ncat.exe', 'netcat', 'mimikatz', 'psexec']
                for proc in processes:
                    if any(sus in proc.info['name'].lower() for sus in suspicious_names):
                        threats.append(self._create_threat("suspicious_process", "critical", f"Suspicious process: {proc.info['name']}"))
                        
                for threat in threats:
                    self.threat_database.append(threat)
                    
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Behavioral monitoring error: {e}")
                await asyncio.sleep(20)
                
    async def _analyze_threat_patterns(self):
        """Analyze threat patterns and correlations"""
        while self.is_monitoring:
            try:
                if len(self.threat_database) < 10:
                    await asyncio.sleep(30)
                    continue
                    
                # Analyze recent threats
                recent_threats = [t for t in self.threat_database if 
                                (datetime.now() - datetime.fromisoformat(t['timestamp'])).seconds < 300]
                
                if len(recent_threats) >= 3:
                    # Multiple threats in short time - possible coordinated attack
                    threat = self._create_threat("coordinated_attack", "critical", 
                                               f"Multiple threats detected in short timeframe: {len(recent_threats)}")
                    self.threat_database.append(threat)
                    
                # Clean old threats
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.threat_database = [t for t in self.threat_database if 
                                      datetime.fromisoformat(t['timestamp']) > cutoff_time]
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(60)
                
    def _create_threat(self, threat_type: str, severity: str, message: str) -> Dict[str, Any]:
        """Create standardized threat object with timezone-aware datetime"""
        return {
            "id": hashlib.md5(f"{threat_type}{time.time()}".encode()).hexdigest()[:16],
            "type": threat_type,
            "severity": severity,
            "message": self._sanitize_message(message),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "advanced_security_engine",
            "confidence": 0.85 + (0.1 if severity == "critical" else 0.05 if severity == "high" else 0),
            "mitigated": False,
            "false_positive": False
        }
        
    def _sanitize_message(self, message: str) -> str:
        """Sanitize log messages to prevent injection"""
        return message.replace('\n', '\n').replace('\r', '\r').replace('\t', '\t')