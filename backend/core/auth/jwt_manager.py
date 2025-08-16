"""
JWT Manager - Authentication Core
Secure JWT token management with enterprise features
"""
import jwt
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry = 3600  # 1 hour
        self.refresh_expiry = 86400  # 24 hours
        self.blacklisted_tokens = set()
        
    def generate_token(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        now_dt = datetime.utcnow()
        now = int(now_dt.timestamp())
        
        # Access token payload
        access_payload = {
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role", "user"),
            "iat": now,
            "exp": now + self.token_expiry,
            "type": "access"
        }
        
        # Refresh token payload
        refresh_payload = {
            "user_id": user_data.get("id"),
            "iat": now,
            "exp": now + self.refresh_expiry,
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.token_expiry,
            "token_type": "Bearer"
        }

    # Convenience for callers/tests that expect a single access token string
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        tokens = self.generate_token(user_data)
        return tokens["access_token"]
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        if token in self.blacklisted_tokens:
            return None
        # Fast pre-check to avoid noisy library exceptions for obviously malformed tokens
        if not token or token.count('.') != 2:
            # reduced to debug to prevent log spam while still traceable
            logger.debug("Invalid token structure (segments)")
            return None
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.info("Expired token rejected")
            return None
        except jwt.InvalidTokenError as e:
            # demote to info to reduce perceived severity for routine invalid tokens
            logger.info(f"Invalid token: {e}")
            return None
            
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
            
        # Generate new access token
        user_data = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
        
        return self.generate_token(user_data)
        
    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        self.blacklisted_tokens.add(token)
        
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user information from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
            
        return {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
        
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
        
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_check.hex() == hash_hex
        except ValueError:
            return False