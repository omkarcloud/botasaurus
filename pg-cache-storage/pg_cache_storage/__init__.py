import json
from hashlib import sha256

__all__ = ['PostgresCacheStorage']


class PostgresCacheStorage:
    """PostgreSQL cache storage using psycopg3."""
    
    def __init__(self, host: str='localhost', port: int=5432, username: str='postgres', password: str='postgres', db_name: str='cache', table_name: str = "botasaurus_cache"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.table_name = table_name
        self._ensure_database()
        self._ensure_table()
    
    def _get_admin_connection(self):
        """Connect to postgres database to perform admin operations."""
        import psycopg
        return psycopg.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            dbname='postgres',
            autocommit=True
        )
    
    def _ensure_database(self):
        """Create the database if it doesn't exist."""
        with self._get_admin_connection() as conn:
            # Check if database exists
            result = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            ).fetchone()
            if not result:
                # Create database (must be outside transaction, hence autocommit=True)
                conn.execute(f'CREATE DATABASE "{self.db_name}"')
    
    def _get_connection(self):
        import psycopg
        from psycopg.rows import dict_row
        return psycopg.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            dbname=self.db_name,
            row_factory=dict_row
        )
    
    def _hash(self, data) -> str:
        """Generate sha256 hash from data."""
        serialized = json.dumps(data).encode('utf-8')
        return sha256(serialized).hexdigest()
    
    def _make_key(self, func_name: str, key_data) -> str:
        """Create cache key from func_name and key_data."""
        return self._hash([func_name, key_data])
    
    def _ensure_table(self):
        """Create cache table if not exists."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS %s (
                    key CHAR(64) PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """ % self.table_name)
            conn.commit()
    
    def get(self, func_name: str, key_data, expires_in=None):
        """
        Returns:
            {"data": value} if cache hit (value can be None)
            None if cache miss or expired
        """
        key = self._make_key(func_name, key_data)
        with self._get_connection() as conn:
            if expires_in is not None:
                row = conn.execute(
                    f"""SELECT data FROM {self.table_name} 
                       WHERE key = %s AND created_at > NOW() - INTERVAL '{expires_in.total_seconds()} seconds'""",
                    (key,)
                ).fetchone()
                if row is None:
                    conn.execute(
                        "DELETE FROM %s WHERE key = %%s" % self.table_name, 
                        (key,)
                    )
                    conn.commit()
                    return None
            else:
                row = conn.execute(
                    "SELECT data FROM %s WHERE key = %%s" % self.table_name,
                    (key,)
                ).fetchone()
            
            if row:
                return {"data": json.loads(row["data"])}
            return None
    
    def put(self, func_name: str, key_data, data) -> None:
        key = self._make_key(func_name, key_data)
        data_json = json.dumps(data)
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO %s (key, data, created_at)
                VALUES (%%s, %%s, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET 
                    data = EXCLUDED.data,
                    created_at = CURRENT_TIMESTAMP
            """ % self.table_name, (key, data_json))
            conn.commit()
    
    def delete(self, func_name: str, key_data) -> None:
        key = self._make_key(func_name, key_data)
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM %s WHERE key = %%s" % self.table_name,
                (key,)
            )
            conn.commit()

    def clear(self) -> None:
        """Delete all entries from the cache table."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM %s" % self.table_name)
            conn.commit()
