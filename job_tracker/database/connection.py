"""
Database connection management for Job Tracker
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator
from ..config import (
    DEFAULT_DB_PATH,
    SEASONS_TABLE_SCHEMA,
    JOBS_TABLE_SCHEMA,
    INDEXES_SCHEMA,
)


class DatabaseConnection:
    """Manages database connections and initialization"""
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables and indexes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(SEASONS_TABLE_SCHEMA)
            cursor.execute(JOBS_TABLE_SCHEMA)
            
            # Create indexes
            for index_sql in INDEXES_SCHEMA:
                cursor.execute(index_sql)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_single_query(self, query: str, params: tuple = ()) -> dict:
        """Execute a SELECT query and return single result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(command, params)
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    
    def execute_many(self, command: str, params_list: list) -> int:
        """Execute multiple commands with different parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(command, params_list)
            conn.commit()
            return cursor.rowcount
