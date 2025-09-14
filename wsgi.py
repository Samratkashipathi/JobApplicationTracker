#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
from pathlib import Path

# Add the application directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Import the Flask application
from app import app

# Ensure database is migrated
from migrate_db import migrate_database

migrate_database()

if __name__ == "__main__":
    app.run()
