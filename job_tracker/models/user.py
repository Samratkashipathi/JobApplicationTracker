"""
User model for Job Tracker
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
import bcrypt


@dataclass
class User:
    """User model for authentication and data isolation"""

    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        """Initialize default values after creation"""
        if self.created_at is None:
            self.created_at = datetime.now()

    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode(
            "utf-8"
        )

    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()

    def to_dict(self, include_password=False) -> dict:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from dictionary"""
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            full_name=data.get("full_name", ""),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            last_login=(
                datetime.fromisoformat(data["last_login"])
                if data.get("last_login")
                else None
            ),
            is_active=data.get("is_active", True),
        )

    def __str__(self) -> str:
        return f"{self.full_name} (@{self.username})"
