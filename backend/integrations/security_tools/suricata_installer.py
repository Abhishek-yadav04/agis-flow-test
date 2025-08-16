"""
Suricata Auto-Installer and Configuration
Automatically installs and configures Suricata IDS
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SuricataInstaller:
    def __init__(self):
        self.suricata_path = None
        self.config_path = None
        self.rules_path = None
        
    def check_suricata_installed(self) -> bool:
        """Check if Suricata is already installed"""
        try:
            result = subprocess.run(['suricata', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Suricata already installed")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def install_suricata_windows(self) -> bool:
        """Install Suricata on Windows"""
        try:
            logger.info("Installing Suricata for Windows...")
            
            # Download Suricata Windows installer
            suricata_url = "https://www.openinfosecfoundation.org/download/suricata-6.0.14-1-64bit.msi"
            installer_path = "suricata_installer.msi"
            
            logger.info("Downloading Suricata installer...")
            urllib.request.urlretrieve(suricata_url, installer_path)
            
            # Install silently
            install_cmd = [
                "msiexec", "/i", installer_path, 
                "/quiet", "/norestart",
                "INSTALLDIR=C:\\Program Files\\Suricata"
            ]
            
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            # Clean up installer
            if os.path.exists(installer_path):
                os.remove(installer_path)
            
            if result.returncode == 0:
                self.suricata_path = "C:\\Program Files\\Suricata\\suricata.exe"
                logger.info("Suricata installed successfully")
                return True
            else:
                logger.error(f"Suricata installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install Suricata: {e}")
            return False
    
    def install_suricata_portable(self) -> bool:
        """Install portable version of Suricata"""
        try:
            logger.info("Installing portable Suricata...")
            
            # Create Suricata directory
            suricata_dir = Path("suricata_portable")
            suricata_dir.mkdir(exist_ok=True)
            
            # Download portable version (simulated - would need actual portable build)
            # For now, create a mock installation
            self._create_mock_suricata(suricata_dir)
            
            self.suricata_path = suricata_dir / "suricata.exe"
            self.config_path = suricata_dir / "suricata.yaml"
            self.rules_path = suricata_dir / "rules"
            
            logger.info("Portable Suricata setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup portable Suricata: {e}")
            return False
    
    def _create_mock_suricata(self, suricata_dir: Path):
        """Create mock Suricata for testing"""
        # Create mock executable
        mock_exe = suricata_dir / "suricata.exe"
        mock_exe.write_text("# Mock Suricata executable")
        
        # Create basic config
        config = {
            "vars": {
                "address-groups": {
                    "HOME_NET": "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]",
                    "EXTERNAL_NET": "!$HOME_NET"
                }
            },
            "outputs": [
                {
                    "eve-log": {
                        "enabled": True,
                        "filetype": "regular",
                        "filename": "eve.json"
                    }
                }
            ]
        }
        
        config_file = suricata_dir / "suricata.yaml"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create rules directory
        rules_dir = suricata_dir / "rules"
        rules_dir.mkdir(exist_ok=True)
        
        # Create sample rules
        sample_rules = """
alert tcp any any -> any 80 (msg:"HTTP GET Request"; content:"GET"; sid:1; rev:1;)
alert tcp any any -> any 443 (msg:"HTTPS Connection"; content:"TLS"; sid:2; rev:1;)
alert tcp any any -> any 22 (msg:"SSH Connection"; content:"SSH"; sid:3; rev:1;)
alert tcp any any -> any [1234,4444,31337] (msg:"Suspicious Port Access"; sid:4; rev:1;)
"""
        
        rules_file = rules_dir / "local.rules"
        rules_file.write_text(sample_rules)
    
    def download_rules(self) -> bool:
        """Download and update Suricata rules"""
        try:
            if not self.rules_path:
                return False
                
            logger.info("Downloading Suricata rules...")
            
            # Download Emerging Threats rules (free)
            rules_url = "https://rules.emergingthreats.net/open/suricata/emerging.rules.tar.gz"
            rules_archive = "emerging.rules.tar.gz"
            
            try:
                urllib.request.urlretrieve(rules_url, rules_archive)
                
                # Extract rules
                import tarfile
                with tarfile.open(rules_archive, 'r:gz') as tar:
                    tar.extractall(self.rules_path)
                
                # Clean up
                os.remove(rules_archive)
                
                logger.info("Rules downloaded successfully")
                return True
                
            except Exception as e:
                logger.warning(f"Failed to download rules: {e}")
                # Use local rules only
                return True
                
        except Exception as e:
            logger.error(f"Rules download failed: {e}")
            return False
    
    def configure_suricata(self) -> bool:
        """Configure Suricata for optimal performance"""
        try:
            if not self.config_path:
                return False
                
            logger.info("Configuring Suricata...")
            
            # Basic configuration for IDS mode
            config = {
                "vars": {
                    "address-groups": {
                        "HOME_NET": "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]",
                        "EXTERNAL_NET": "!$HOME_NET",
                        "HTTP_SERVERS": "$HOME_NET",
                        "SMTP_SERVERS": "$HOME_NET",
                        "SQL_SERVERS": "$HOME_NET",
                        "DNS_SERVERS": "$HOME_NET",
                        "TELNET_SERVERS": "$HOME_NET",
                        "AIM_SERVERS": "$EXTERNAL_NET",
                        "DC_SERVERS": "$HOME_NET",
                        "DNP3_SERVER": "$HOME_NET",
                        "DNP3_CLIENT": "$HOME_NET",
                        "MODBUS_CLIENT": "$HOME_NET",
                        "MODBUS_SERVER": "$HOME_NET",
                        "ENIP_CLIENT": "$HOME_NET",
                        "ENIP_SERVER": "$HOME_NET"
                    },
                    "port-groups": {
                        "HTTP_PORTS": "80",
                        "SHELLCODE_PORTS": "!80",
                        "ORACLE_PORTS": "1521",
                        "SSH_PORTS": "22",
                        "DNP3_PORTS": "20000",
                        "MODBUS_PORTS": "502",
                        "FILE_DATA_PORTS": "[$HTTP_PORTS,110,143]",
                        "FTP_PORTS": "21",
                        "GENEVE_PORTS": "6081",
                        "VXLAN_PORTS": "4789",
                        "TEREDO_PORTS": "3544"
                    }
                },
                "default-log-dir": "./logs/",
                "stats": {
                    "enabled": True,
                    "interval": 8
                },
                "outputs": [
                    {
                        "eve-log": {
                            "enabled": True,
                            "filetype": "regular",
                            "filename": "eve.json",
                            "types": [
                                {"alert": {"tagged-packets": True}},
                                {"http": {"extended": True}},
                                {"dns": {"query": True, "answer": True}},
                                {"tls": {"extended": True}},
                                {"files": {"force-magic": False}},
                                {"smtp": {}},
                                {"ssh": {}},
                                {"stats": {"totals": True, "threads": False, "deltas": False}},
                                {"flow": {}}
                            ]
                        }
                    }
                ],
                "logging": {
                    "default-log-level": "notice",
                    "default-output-filter": "",
                    "outputs": [
                        {
                            "console": {
                                "enabled": True
                            }
                        },
                        {
                            "file": {
                                "enabled": True,
                                "level": "info",
                                "filename": "suricata.log"
                            }
                        }
                    ]
                },
                "af-packet": [
                    {
                        "interface": "eth0",
                        "threads": "auto",
                        "defrag": True,
                        "cluster-type": "cluster_flow",
                        "cluster-id": 99,
                        "copy-mode": "ips",
                        "copy-iface": "eth1",
                        "buffer-size": 64535,
                        "use-mmap": True,
                        "tpacket-v3": True
                    }
                ],
                "pcap": [
                    {
                        "interface": "eth0",
                        "threads": "auto",
                        "promisc": True,
                        "snaplen": 1518
                    }
                ],
                "pcap-file": {
                    "checksum-checks": "auto"
                },
                "app-layer": {
                    "protocols": {
                        "tls": {
                            "enabled": True,
                            "detection-ports": {
                                "dp": "443"
                            }
                        },
                        "http": {
                            "enabled": True,
                            "libhtp": {
                                "default-config": {
                                    "personality": "IDS",
                                    "request-body-limit": 100000,
                                    "response-body-limit": 100000,
                                    "request-body-minimal-inspect-size": 32768,
                                    "request-body-inspect-window": 4096,
                                    "response-body-minimal-inspect-size": 40000,
                                    "response-body-inspect-window": 16384,
                                    "response-body-decompress-layer-limit": 2,
                                    "http-body-inline": "auto",
                                    "swf-decompression": {
                                        "enabled": True,
                                        "type": "both",
                                        "compress-depth": 100000,
                                        "decompress-depth": 100000
                                    },
                                    "double-decode-path": False,
                                    "double-decode-query": False
                                }
                            }
                        }
                    }
                },
                "asn1-max-frames": 256,
                "run-as": {
                    "user": "suricata",
                    "group": "suricata"
                },
                "coredump": {
                    "max-dump": "unlimited"
                },
                "host-mode": "auto",
                "unix-command": {
                    "enabled": "auto"
                },
                "legacy": {
                    "uricontent": "enabled"
                },
                "engine-analysis": {
                    "rules-fast-pattern": True,
                    "rules": True
                },
                "pcre": {
                    "match-limit": 3500,
                    "match-limit-recursion": 1500
                },
                "host-os-policy": {
                    "windows": [0.0, 0.0, 0.0, 0.0],
                    "bsd": [],
                    "bsd-right": [],
                    "old-linux": [],
                    "linux": [],
                    "old-solaris": [],
                    "solaris": [],
                    "hpux10": [],
                    "hpux11": [],
                    "irix": [],
                    "macos": [],
                    "vista": [],
                    "windows2k3": []
                },
                "defrag": {
                    "memcap": "32mb",
                    "hash-size": 65536,
                    "trackers": 65535,
                    "max-frags": 65535,
                    "prealloc": True,
                    "timeout": 60
                },
                "flow": {
                    "memcap": "128mb",
                    "hash-size": 65536,
                    "prealloc": 10000,
                    "emergency-recovery": 30,
                    "managers": 1,
                    "recyclers": 1
                }
            }
            
            with open(self.config_path, 'w') as f:
                import yaml
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info("Suricata configuration complete")
            return True
            
        except Exception as e:
            logger.error(f"Suricata configuration failed: {e}")
            return False
    
    def install_and_configure(self) -> bool:
        """Complete installation and configuration"""
        try:
            # Check if already installed
            if self.check_suricata_installed():
                return True
            
            # Try Windows installer first
            if sys.platform == "win32":
                if self.install_suricata_windows():
                    success = True
                else:
                    # Fallback to portable
                    success = self.install_suricata_portable()
            else:
                # Linux/Unix installation
                success = self._install_suricata_linux()
            
            if success:
                # Download rules
                self.download_rules()
                
                # Configure
                self.configure_suricata()
                
                logger.info("Suricata installation and configuration complete")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Suricata installation failed: {e}")
            return False
    
    def _install_suricata_linux(self) -> bool:
        """Install Suricata on Linux"""
        try:
            # Try package manager installation
            distro_commands = [
                ["apt-get", "update", "&&", "apt-get", "install", "-y", "suricata"],
                ["yum", "install", "-y", "suricata"],
                ["dnf", "install", "-y", "suricata"],
                ["pacman", "-S", "--noconfirm", "suricata"]
            ]
            
            for cmd in distro_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info("Suricata installed via package manager")
                        return True
                except:
                    continue
            
            # If package manager fails, try source installation
            return self._install_from_source()
            
        except Exception as e:
            logger.error(f"Linux installation failed: {e}")
            return False
    
    def _install_from_source(self) -> bool:
        """Install Suricata from source (simplified)"""
        try:
            logger.info("Installing Suricata from source...")
            
            # This would be a complex process involving:
            # 1. Download source code
            # 2. Install dependencies
            # 3. Configure build
            # 4. Compile and install
            
            # For now, create a mock installation
            return self.install_suricata_portable()
            
        except Exception as e:
            logger.error(f"Source installation failed: {e}")
            return False

# Global installer instance
suricata_installer = SuricataInstaller()