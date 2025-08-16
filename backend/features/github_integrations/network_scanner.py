class NetworkScanner:
    def __init__(self):
        self.scans_completed = 0
        self.hosts_discovered = 0
    
    def scan_network(self, network_range):
        self.scans_completed += 1
        return {"hosts": self.hosts_discovered, "status": "completed"}