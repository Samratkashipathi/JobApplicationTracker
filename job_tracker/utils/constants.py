"""
Constants for Job Tracker
"""

import os

# Database Configuration
DEFAULT_DB_PATH = os.path.join(os.getcwd(), "job_tracker.db")

# Job Status Options
JOB_STATUSES = [
    "Applied",
    "Phone Screen",
    "Technical Interview",
    "Onsite Interview",
    "Final Interview",
    "Offer",
    "Rejected",
    "Withdrawn",
    "On Hold",
]

# Display Configuration
TABLE_FORMAT = "grid"
MAX_DISPLAY_LENGTH = 30

# Application Information
APP_NAME = "Job Application Tracker"
APP_VERSION = "1.0.0"
