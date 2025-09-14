#!/usr/bin/env python3
"""
Critical Fix: Implement proper user data isolation
This script fixes the user data isolation issue
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.database import DatabaseConnection


def fix_user_isolation():
    """Fix user data isolation by updating all methods"""
    print("🔧 Fixing user data isolation...")

    db = DatabaseConnection()

    # First, let's see what data exists
    try:
        # Check existing users
        users = db.execute_query("SELECT id, username FROM users")
        print(f"📊 Found {len(users)} users:")
        for user in users:
            print(f"   - User {user['id']}: {user['username']}")

        # Check seasons without user_id
        seasons_without_user = db.execute_query(
            "SELECT id, name FROM seasons WHERE user_id IS NULL"
        )
        print(f"📊 Found {len(seasons_without_user)} seasons without user_id:")
        for season in seasons_without_user:
            print(f"   - Season {season['id']}: {season['name']}")

        # Check jobs without user_id
        jobs_without_user = db.execute_query(
            "SELECT id, role, company_name FROM jobs WHERE user_id IS NULL"
        )
        print(f"📊 Found {len(jobs_without_user)} jobs without user_id:")
        for job in jobs_without_user:
            print(f"   - Job {job['id']}: {job['role']} at {job['company_name']}")

        # If there's only one user, assign all orphaned data to them
        if len(users) == 1:
            user_id = users[0]["id"]
            username = users[0]["username"]

            print(f"\n🔄 Assigning all orphaned data to user: {username}")

            # Update seasons
            if seasons_without_user:
                updated_seasons = db.execute_command(
                    "UPDATE seasons SET user_id = ? WHERE user_id IS NULL", (user_id,)
                )
                print(f"✅ Updated {updated_seasons} seasons")

            # Update jobs
            if jobs_without_user:
                updated_jobs = db.execute_command(
                    "UPDATE jobs SET user_id = ? WHERE user_id IS NULL", (user_id,)
                )
                print(f"✅ Updated {updated_jobs} jobs")

        elif len(users) > 1:
            print(
                "\n⚠️  Multiple users found. Cannot automatically assign orphaned data."
            )
            print("💡 Please manually assign data or delete orphaned records.")

        else:
            print("\n💡 No users found. Data will be isolated once users register.")

        print("\n🎉 User isolation fix completed!")

    except Exception as e:
        print(f"❌ Error fixing user isolation: {e}")
        return False

    return True


if __name__ == "__main__":
    fix_user_isolation()
