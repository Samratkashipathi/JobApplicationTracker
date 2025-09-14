"""
Job model for Job Tracker
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from .enums import JobStatus


@dataclass
class Job:
    """Job application model"""
    
    id: Optional[int] = None
    season_id: Optional[int] = None
    role: str = ""
    company_name: str = ""
    company_website: Optional[str] = None
    source: Optional[str] = None
    current_status: JobStatus = JobStatus.APPLIED
    job_description: Optional[str] = None
    resume_sent: Optional[str] = None
    applied_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    season_name: Optional[str] = None  # For joined queries
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.applied_date is None:
            self.applied_date = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        
        # Convert string status to JobStatus enum if needed
        if isinstance(self.current_status, str):
            self.current_status = JobStatus.from_string(self.current_status)
    
    def update_status(self, new_status: JobStatus):
        """Update job status and last_updated timestamp"""
        self.current_status = new_status
        self.last_updated = datetime.now()
    
    @property
    def days_since_applied(self) -> int:
        """Get number of days since application"""
        if not self.applied_date:
            return 0
        return (datetime.now() - self.applied_date).days
    
    @property
    def days_since_updated(self) -> int:
        """Get number of days since last update"""
        if not self.last_updated:
            return 0
        return (datetime.now() - self.last_updated).days
    
    def to_dict(self) -> dict:
        """Convert job to dictionary"""
        return {
            "id": self.id,
            "season_id": self.season_id,
            "role": self.role,
            "company_name": self.company_name,
            "company_website": self.company_website,
            "source": self.source,
            "current_status": self.current_status.value,
            "job_description": self.job_description,
            "resume_sent": self.resume_sent,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "season_name": self.season_name,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create Job from dictionary"""
        return cls(
            id=data.get("id"),
            season_id=data.get("season_id"),
            role=data.get("role", ""),
            company_name=data.get("company_name", ""),
            company_website=data.get("company_website"),
            source=data.get("source"),
            current_status=JobStatus.from_string(data.get("current_status", "Applied")),
            job_description=data.get("job_description"),
            resume_sent=data.get("resume_sent"),
            applied_date=datetime.fromisoformat(data["applied_date"]) if data.get("applied_date") else None,
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
            season_name=data.get("season_name"),
        )
    
    def __str__(self) -> str:
        return f"{self.role} at {self.company_name} ({self.current_status.value})"
