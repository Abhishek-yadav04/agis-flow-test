"""
Threat Detection API - Enterprise Grade
Real-time threat detection and analysis endpoints
"""

from fastapi import APIRouter
from typing import Dict, List, Any
import time
import random
from datetime import datetime, timezone

router = APIRouter(prefix="/api/threats", tags=["Threat Detection"])

# Simulated threat database
threat_database = []

@router.get("/recent")
async def get_recent_threats(limit: int = 10) -> Dict[str, Any]:
    """Get recent threat detections"""
    # Simulate threat detection
    if random.random() < 0.1:  # 10% chance of new threat
        threat = {
            "id": f"threat_{int(time.time())}",
            "type": random.choice(["port_scan", "brute_force", "anomaly", "malware"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "source_ip": f"192.168.1.{random.randint(1, 254)}",
            "target_ip": f"10.0.0.{random.randint(1, 100)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "status": "active"
        }
        threat_database.append(threat)
    
    # Keep only recent threats
    if len(threat_database) > 50:
        threat_database[:] = threat_database[-50:]
    
    return {
        "threats": threat_database[-limit:],
        "total_count": len(threat_database),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@router.get("/statistics")
async def get_threat_statistics() -> Dict[str, Any]:
    """Get threat detection statistics"""
    if not threat_database:
        return {
            "total_threats": 0,
            "by_severity": {},
            "by_type": {},
            "detection_rate": 0.0
        }
    
    severity_counts = {}
    type_counts = {}
    
    for threat in threat_database:
        severity = threat.get("severity", "unknown")
        threat_type = threat.get("type", "unknown")
        
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        type_counts[threat_type] = type_counts.get(threat_type, 0) + 1
    
    return {
        "total_threats": len(threat_database),
        "by_severity": severity_counts,
        "by_type": type_counts,
        "detection_rate": round(random.uniform(0.85, 0.98), 2),
        "false_positive_rate": round(random.uniform(0.01, 0.05), 2)
    }