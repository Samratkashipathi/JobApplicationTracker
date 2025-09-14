"""
Configuration module for Job Tracker
Contains application configuration and settings.
"""

import os
from pathlib import Path

# Database Configuration
DEFAULT_DB_NAME = "job_tracker.db"
DEFAULT_DB_PATH = os.path.join(os.getcwd(), DEFAULT_DB_NAME)

# Application Configuration
APP_NAME = "Job Application Tracker"
APP_VERSION = "1.0.0"

# UI Configuration
TABLE_FORMAT = "grid"
MAX_DISPLAY_LENGTH = 30


# Colors (for terminal output)
class Colors:
    SUCCESS = "\033[92m"
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    INFO = "\033[94m"
    HEADER = "\033[96m"
    RESET = "\033[0m"


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

# Database Schema Configuration
SEASONS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    start_date TEXT NOT NULL,
    end_date TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

JOBS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    company_name TEXT NOT NULL,
    company_website TEXT,
    source TEXT,
    current_status TEXT NOT NULL DEFAULT 'Applied',
    job_description TEXT,
    resume_sent TEXT,
    applied_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons (id) ON DELETE CASCADE
)
"""

INDEXES_SCHEMA = [
    "CREATE INDEX IF NOT EXISTS idx_seasons_active ON seasons (is_active)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_season ON jobs (season_id)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (current_status)",
]
