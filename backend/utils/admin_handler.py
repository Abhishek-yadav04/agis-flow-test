"""
Admin Privilege Handler
Handles admin privilege requests without infinite loops
"""

import os
import ctypes
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AdminPrivilegeHandler:
    """Handle admin privilege requests safely"""
    
    def __init__(self):
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            if os.name == 'nt':  # Windows
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:  # Unix-like
                return os.geteuid() == 0
        except Exception:
            return False
    
    def get_privilege_status(self) -> Dict[str, Any]:
        """Get current privilege status"""
        return {
            "is_admin": self.is_admin,
            "platform": os.name,
            "features_available": self._get_admin_features() if self.is_admin else self._get_limited_features(),
            "capture_mode": "real" if self.is_admin else "simulation"
        }
    
    def _get_admin_features(self) -> Dict[str, bool]:
        """Get features available with admin privileges"""
        return {
            "real_packet_capture": True,
            "system_level_monitoring": True,
            "network_interface_access": True,
            "process_monitoring": True
        }
    
    def _get_limited_features(self) -> Dict[str, bool]:
        """Get features available without admin privileges"""
        return {
            "real_packet_capture": False,
            "system_level_monitoring": False,
            "network_interface_access": False,
            "process_monitoring": True
        }

admin_handler = AdminPrivilegeHandler()