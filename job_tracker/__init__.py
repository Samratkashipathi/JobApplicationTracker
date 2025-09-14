"""
Job Application Tracker Package
A modular job application tracking system.
"""

__version__ = "1.0.0"
__author__ = "Job Tracker Team"

from .models import Season, Job, JobStatus
from .services import JobTrackerService
from .ui import JobTrackerCLI

__all__ = ["Season", "Job", "JobStatus", "JobTrackerService", "JobTrackerCLI"]
