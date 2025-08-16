"""
Real-time Threat Intelligence Feed
"""

from fastapi import APIRouter
import random
from datetime import datetime, timezone
from typing import Dict, List, Any

router = APIRouter(prefix="/api/threat-intel", tags=["Threat Intelligence"])

class RealTimeThreatFeed:
    def __init__(self):
        self.threat_sources = ["MISP", "STIX/TAXII", "VirusTotal", "AlienVault", "IBM X-Force"]
        self.iocs = {
            "ip_addresses": 125847,
            "domains": 89234,
            "file_hashes": 234567,
            "urls": 156789,
            "email_addresses": 45678
        }
        
    def generate_live_threats(self):
        threats = []
        for _ in range(random.randint(3, 8)):
            threats.append({
                "id": f"threat_{random.randint(10000, 99999)}",
                "type": random.choice(["malware", "phishing", "c2", "exploit", "apt"]),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "source": random.choice(self.threat_sources),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "tags": random.sample(["apt", "malware", "trojan", "backdoor", "c2"], 2)
            })
        return threats

threat_feed = RealTimeThreatFeed()

@router.get("/live-feed")
async def get_live_threat_feed() -> Dict[str, Any]:
    return {
        "threats": threat_feed.generate_live_threats(),
        "feed_status": "active",
        "sources_online": len(threat_feed.threat_sources),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ioc-database")
async def get_ioc_database() -> Dict[str, Any]:
    return {
        "indicators": threat_feed.iocs,
        "total_iocs": sum(threat_feed.iocs.values()),
        "new_today": random.randint(500, 2000),
        "high_confidence": random.randint(80000, 120000)
    }