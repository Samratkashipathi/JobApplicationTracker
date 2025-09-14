"""
User Repository for Job Tracker
Handles database operations for users
"""

from typing import List, Optional
from ..models.user import User
from .connection import DatabaseConnection


class UserRepository:
    """Repository for user data operations"""

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self._create_table()

    def _create_table(self):
        """Create users table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """
        self.db.execute_command(create_table_sql)

        # Create indexes for performance
        self.db.execute_command(
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
        )
        self.db.execute_command(
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
        )

    def create(self, user: User) -> int:
        """Create new user"""
        insert_sql = """
        INSERT INTO users (username, email, password_hash, full_name)
        VALUES (?, ?, ?, ?)
        """
        try:
            return self.db.execute_command(
                insert_sql,
                (user.username, user.email, user.password_hash, user.full_name),
            )
        except Exception as e:
            error_str = str(e).lower()
            if "unique constraint failed: users.username" in error_str:
                raise ValueError("Username already exists")
            elif "unique constraint failed: users.email" in error_str:
                raise ValueError("Email already exists")
            else:
                raise e

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ? AND is_active = TRUE"
        result = self.db.execute_single_query(query, (user_id,))
        return self._row_to_user(result) if result else None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = ? AND is_active = TRUE"
        result = self.db.execute_single_query(query, (username,))
        return self._row_to_user(result) if result else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ? AND is_active = TRUE"
        result = self.db.execute_single_query(query, (email,))
        return self._row_to_user(result) if result else None

    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        query = "SELECT id FROM users WHERE username = ?"
        result = self.db.execute_single_query(query, (username,))
        return result is not None

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        query = "SELECT id FROM users WHERE email = ?"
        result = self.db.execute_single_query(query, (email,))
        return result is not None

    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        rows_affected = self.db.execute_command(query, (user_id,))
        return rows_affected > 0

    def update_user(self, user: User) -> bool:
        """Update user information"""
        query = """
        UPDATE users 
        SET email = ?, full_name = ?, password_hash = ?
        WHERE id = ?
        """
        rows_affected = self.db.execute_command(
            query, (user.email, user.full_name, user.password_hash, user.id)
        )
        return rows_affected > 0

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user (soft delete)"""
        query = "UPDATE users SET is_active = FALSE WHERE id = ?"
        rows_affected = self.db.execute_command(query, (user_id,))
        return rows_affected > 0

    def get_all_active(self) -> List[User]:
        """Get all active users"""
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
        results = self.db.execute_query(query)
        return [self._row_to_user(row) for row in results]

    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        if not row:
            return None

        from datetime import datetime

        # Handle datetime conversion
        created_at = row.get("created_at")
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = None

        last_login = row.get("last_login")
        if last_login and isinstance(last_login, str):
            try:
                last_login = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
            except:
                last_login = None

        return User(
            id=row.get("id"),
            username=row.get("username", ""),
            email=row.get("email", ""),
            password_hash=row.get("password_hash", ""),
            full_name=row.get("full_name", ""),
            created_at=created_at,
            last_login=last_login,
            is_active=bool(row.get("is_active", True)),
        )
