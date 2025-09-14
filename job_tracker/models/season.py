"""
Season model for Job Tracker
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Season:
    """Season model representing a job hunting period"""

    id: Optional[int] = None
    name: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values after creation"""
        if self.start_date is None:
            self.start_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_ended(self) -> bool:
        """Check if the season has ended"""
        return self.end_date is not None

    @property
    def duration_days(self) -> Optional[int]:
        """Get the duration of the season in days"""
        if not self.start_date:
            return None

        end_time = self.end_date or datetime.now()
        return (end_time - self.start_date).days

    def end_season(self):
        """End the current season"""
        self.end_date = datetime.now()
        self.is_active = False

    def to_dict(self) -> dict:
        """Convert season to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": 1 if self.is_active else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Season":
        """Create Season from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            start_date=(
                datetime.fromisoformat(data["start_date"])
                if data.get("start_date")
                else None
            ),
            end_date=(
                datetime.fromisoformat(data["end_date"])
                if data.get("end_date")
                else None
            ),
            is_active=bool(data.get("is_active", True)),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
        )

    def __str__(self) -> str:
        status = "Active" if self.is_active else "Ended"
        return f"Season: {self.name} ({status})"
