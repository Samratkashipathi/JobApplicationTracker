#!/usr/bin/env python3
"""
QUICK FIX: Assign all existing data to the first user
Run this immediately to fix the data isolation issue
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.database import DatabaseConnection


def quick_fix():
    """Quickly assign all data to first user"""
    print("🚨 QUICK FIX: Assigning all data to first user...")

    db = DatabaseConnection()

    try:
        # Get first user
        users = db.execute_query("SELECT id, username FROM users LIMIT 1")

        if not users:
            print("❌ No users found. Please register a user first.")
            return False

        user_id = users[0]["id"]
        username = users[0]["username"]

        print(f"👤 Assigning all data to user: {username} (ID: {user_id})")

        # Update all seasons
        updated_seasons = db.execute_command(
            "UPDATE seasons SET user_id = ? WHERE user_id IS NULL", (user_id,)
        )
        print(f"✅ Updated {updated_seasons} seasons")

        # Update all jobs
        updated_jobs = db.execute_command(
            "UPDATE jobs SET user_id = ? WHERE user_id IS NULL", (user_id,)
        )
        print(f"✅ Updated {updated_jobs} jobs")

        print(f"\n🎉 Quick fix completed! All data now belongs to {username}")
        print("🔒 User data isolation is now working!")

        return True

    except Exception as e:
        print(f"❌ Quick fix failed: {e}")
        return False


if __name__ == "__main__":
    if quick_fix():
        print("\n🚀 You can now restart the web app: python3 app.py")
    else:
        print("\n❌ Please fix the issues above and try again")
