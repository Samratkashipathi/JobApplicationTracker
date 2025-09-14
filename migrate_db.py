#!/usr/bin/env python3
"""
Database migration script to add user support
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.database import DatabaseConnection


def migrate_database():
    """Add user_id columns to existing tables"""
    db = DatabaseConnection()
    
    print("Starting database migration...")
    
    try:
        # Add user_id column to seasons table
        try:
            db.execute_command("ALTER TABLE seasons ADD COLUMN user_id INTEGER")
            print("✅ Added user_id column to seasons table")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"❌ Error adding user_id to seasons: {e}")
            else:
                print("ℹ️  user_id column already exists in seasons table")
        
        # Add user_id column to jobs table  
        try:
            db.execute_command("ALTER TABLE jobs ADD COLUMN user_id INTEGER")
            print("✅ Added user_id column to jobs table")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"❌ Error adding user_id to jobs: {e}")
            else:
                print("ℹ️  user_id column already exists in jobs table")
        
        # Create indexes for performance
        try:
            db.execute_command("CREATE INDEX IF NOT EXISTS idx_seasons_user_id ON seasons(user_id)")
            db.execute_command("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
            print("✅ Created indexes for user_id columns")
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
        
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
