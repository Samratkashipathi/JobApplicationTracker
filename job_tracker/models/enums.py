"""
Enums for Job Tracker models
"""

from enum import Enum


class JobStatus(Enum):
    """Job application status enumeration"""
    
    APPLIED = "Applied"
    PHONE_SCREEN = "Phone Screen"
    TECHNICAL_INTERVIEW = "Technical Interview"
    ONSITE_INTERVIEW = "Onsite Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"
    ON_HOLD = "On Hold"
    
    @classmethod
    def get_all_statuses(cls):
        """Get all job status values as a list"""
        return [status.value for status in cls]
    
    @classmethod
    def from_string(cls, status_str: str):
        """Get JobStatus enum from string value"""
        for status in cls:
            if status.value == status_str:
                return status
        raise ValueError(f"Invalid job status: {status_str}")
    
    def __str__(self):
        return self.value
