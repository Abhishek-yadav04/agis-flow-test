"""
Database Manager - Core Database Operations
Professional database management with connection pooling and security
"""
import sqlite3
import asyncio
import threading
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/enterprise.db", pool_size: int = 10):
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.stats = {
            "queries_executed": 0,
            "connections_created": 0,
            "errors": 0,
            "avg_query_time": 0
        }
        self._initialize_database()
        self._create_connection_pool()
        
    def _initialize_database(self):
        """Initialize database with security settings and error handling"""
        try:
            self.db_path.parent.mkdir(exist_ok=True, mode=0o700)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=FULL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA secure_delete=ON")
                conn.execute("PRAGMA temp_store=MEMORY")
                
                # Create core tables
                self._create_tables(conn)
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
            
    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                config TEXT,
                results TEXT,
                accuracy REAL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS threats (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                target_ip TEXT,
                message TEXT NOT NULL,
                details TEXT,
                status TEXT DEFAULT 'active',
                confidence REAL,
                mitre_technique TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS blockchain_transactions (
                id TEXT PRIMARY KEY,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                gas_used INTEGER,
                block_hash TEXT,
                transaction_hash TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS quantum_keys (
                id TEXT PRIMARY KEY,
                key_data TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                key_length INTEGER,
                security_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            conn.execute(table_sql)
            
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(type)",
            "CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics(metric_type)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
            
        conn.commit()
        
    def _create_connection_pool(self):
        """Create connection pool"""
        with self.pool_lock:
            for _ in range(self.pool_size):
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connection_pool.append(conn)
                self.stats["connections_created"] += 1
                
    @contextmanager
    def get_connection(self):
        """Get connection from pool with proper resource management"""
        conn = None
        try:
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()
                else:
                    conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    self.stats["connections_created"] += 1
                    
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    # If rollback itself fails, ensure we don't hide original error
                    logger.debug("Rollback failed during connection error cleanup", exc_info=True)
            raise
        finally:
            if conn:
                try:
                    with self.pool_lock:
                        if len(self.connection_pool) < self.pool_size:
                            self.connection_pool.append(conn)
                        else:
                            conn.close()
                except Exception as e:
                    logger.error(f"Connection cleanup error: {e}")
                        
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                
            self.stats["queries_executed"] += 1
            query_time = time.time() - start_time
            self._update_avg_query_time(query_time)
            
            return results
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Query execution error: {e}")
            raise
            
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                rows_affected = cursor.rowcount
                
            self.stats["queries_executed"] += 1
            query_time = time.time() - start_time
            self._update_avg_query_time(query_time)
            
            return rows_affected
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Update execution error for query {query[:50]}...: {e}")
            raise
            
    def execute_batch(self, query: str, params_list: List[Tuple]) -> int:
        """Execute batch operations"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                rows_affected = cursor.rowcount
                
            self.stats["queries_executed"] += len(params_list)
            query_time = time.time() - start_time
            self._update_avg_query_time(query_time)
            
            return rows_affected
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Batch execution error: {e}")
            raise
            
    def _update_avg_query_time(self, query_time: float):
        """Update average query time"""
        if self.stats["queries_executed"] == 1:
            self.stats["avg_query_time"] = query_time
        else:
            self.stats["avg_query_time"] = (
                (self.stats["avg_query_time"] * (self.stats["queries_executed"] - 1) + query_time) /
                self.stats["queries_executed"]
            )
            
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create new user"""
        query = '''INSERT INTO users (id, username, email, password_hash, role)
                   VALUES (?, ?, ?, ?, ?)'''
        params = (
            user_data["id"],
            user_data["username"],
            user_data["email"],
            user_data["password_hash"],
            user_data.get("role", "user")
        )
        self.execute_update(query, params)
        return user_data["id"]
        
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username with SQL injection protection"""
        if not username or not isinstance(username, str):
            return None
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        try:
            results = self.execute_query(query, (username,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"User query failed: {e}")
            return None
        
    def log_audit_event(self, user_id: str, action: str, resource: str = None, 
                       details: str = None, ip_address: str = None):
        """Log audit event"""
        query = '''INSERT INTO audit_logs (user_id, action, resource, details, ip_address)
                   VALUES (?, ?, ?, ?, ?)'''
        params = (user_id, action, resource, details, ip_address)
        self.execute_update(query, params)
        
    def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create user session"""
        query = '''INSERT INTO sessions (id, user_id, token_hash, expires_at, ip_address, user_agent)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        params = (
            session_data["id"],
            session_data["user_id"],
            session_data["token_hash"],
            session_data["expires_at"],
            session_data.get("ip_address"),
            session_data.get("user_agent")
        )
        self.execute_update(query, params)
        return session_data["id"]
        
    def get_active_session(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Get active session by token"""
        query = '''SELECT * FROM sessions WHERE token_hash = ? 
                   AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP'''
        results = self.execute_query(query, (token_hash,))
        return results[0] if results else None
        
    def store_threat(self, threat_data: Dict[str, Any]) -> str:
        """Store threat detection"""
        query = '''INSERT INTO threats (id, type, severity, source_ip, target_ip, 
                   message, details, confidence, mitre_technique)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (
            threat_data["id"],
            threat_data["type"],
            threat_data["severity"],
            threat_data.get("source_ip"),
            threat_data.get("target_ip"),
            threat_data["message"],
            json.dumps(threat_data.get("details", {})),
            threat_data.get("confidence"),
            threat_data.get("mitre_technique")
        )
        self.execute_update(query, params)
        return threat_data["id"]
        
    def get_recent_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent threats"""
        query = '''SELECT * FROM threats ORDER BY detected_at DESC LIMIT ?'''
        return self.execute_query(query, (limit,))
        
    def store_system_metric(self, metric_type: str, metric_name: str, 
                          value: float, unit: str = None):
        """Store system metric"""
        query = '''INSERT INTO system_metrics (metric_type, metric_name, value, unit)
                   VALUES (?, ?, ?, ?)'''
        params = (metric_type, metric_name, value, unit)
        self.execute_update(query, params)
        
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        table_counts = {}
        tables = ["users", "sessions", "audit_logs", "experiments", "threats", 
                 "system_metrics", "blockchain_transactions", "quantum_keys"]
        
        for table in tables:
            try:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                table_counts[table] = result[0]["count"]
            except Exception:
                table_counts[table] = 0
                
        return {
            **self.stats,
            "table_counts": table_counts,
            "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "connection_pool_size": len(self.connection_pool)
        }
        
    def cleanup_old_data(self, days: int = 30):
        """Cleanup old data with parameterized queries"""
        queries = [
            ("DELETE FROM audit_logs WHERE timestamp < datetime('now', '-' || ? || ' days')", (days,)),
            ("DELETE FROM sessions WHERE expires_at < datetime('now', '-' || ? || ' days')", (days,)),
            ("DELETE FROM system_metrics WHERE timestamp < datetime('now', '-' || ? || ' days')", (days,))
        ]
        
        for query, params in queries:
            try:
                self.execute_update(query, params)
            except Exception as e:
                logger.error(f"Cleanup error for query {query}: {e}")
                
    def close_all_connections(self):
        """Close all connections in pool"""
        with self.pool_lock:
            for conn in self.connection_pool:
                conn.close()
            self.connection_pool.clear()

# Global database manager instance
db_manager = DatabaseManager()