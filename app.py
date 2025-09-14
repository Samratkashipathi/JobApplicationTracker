#!/usr/bin/env python3
"""
Job Application Tracker - Web Application
A beautiful web interface for tracking job applications across different seasons.
"""

import sys
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from migrate_db import migrate_database

# Add the current directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.services import JobTrackerService
from job_tracker.models import JobStatus
from auth_utils import auth_manager

app = Flask(__name__)
CORS(app)

# Configure Flask session
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "your-secret-key-change-in-production"
)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)

# Production security settings
if os.getenv("FLASK_ENV") == "production":
    app.config["SESSION_COOKIE_SECURE"] = True  # HTTPS only
    app.config["SESSION_COOKIE_HTTPONLY"] = True  # No JS access
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection

# Initialize session
Session(app)

# Initialize the job tracker service
try:
    job_service = JobTrackerService()
    print("✅ Job tracker service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize job tracker service: {e}")
    job_service = None


@app.route("/")
def index():
    """Main dashboard page"""
    try:
        is_logged_in = auth_manager.is_logged_in()
        print(f"🔍 Index route: User logged in = {is_logged_in}")

        if not is_logged_in:
            print("🔄 Redirecting to login page")
            return redirect(url_for("login_page"))

        print("✅ Serving dashboard")
        return render_template("index.html")
    except Exception as e:
        print(f"❌ Error in index route: {e}")
        return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    """Login/Registration page"""
    try:
        is_logged_in = auth_manager.is_logged_in()
        print(f"🔍 Login route: User logged in = {is_logged_in}")

        if is_logged_in:
            print("🔄 User already logged in, redirecting to dashboard")
            return redirect(url_for("index"))

        print("✅ Serving login page")
        return render_template("auth.html")
    except Exception as e:
        print(f"❌ Error in login route: {e}")
        # Return a simple login page if there's an error
        return render_template("auth.html")


@app.route("/logout")
def logout():
    """Logout user"""
    auth_manager.logout_user()
    return redirect(url_for("login_page"))


# Authentication API Routes
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip()

        success, message, user = auth_manager.register_user(
            username, email, password, full_name
        )

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Registration failed: {str(e)}"}),
            500,
        )


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")

        success, message, user = auth_manager.login_user(username, password)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": message,
                    "user": user.to_dict() if user else None,
                }
            )
        else:
            return jsonify({"success": False, "error": message}), 401

    except Exception as e:
        return jsonify({"success": False, "error": f"Login failed: {str(e)}"}), 500


@app.route("/api/auth/user", methods=["GET"])
@auth_manager.require_login
def get_current_user():
    """Get current user information"""
    user = auth_manager.get_current_user()
    if user:
        return jsonify({"success": True, "data": user.to_dict()})
    else:
        return jsonify({"success": False, "error": "User not found"}), 404


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Get authentication status"""
    try:
        is_logged_in = auth_manager.is_logged_in()
        user = auth_manager.get_current_user() if is_logged_in else None

        print(
            f"🔍 Auth status API: logged_in = {is_logged_in}, user = {user.username if user else None}"
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "logged_in": is_logged_in,
                    "user": user.to_dict() if user else None,
                },
            }
        )
    except Exception as e:
        print(f"❌ Error in auth status API: {e}")
        return jsonify(
            {
                "success": True,
                "data": {
                    "logged_in": False,
                    "user": None,
                },
            }
        )


@app.route("/api/seasons", methods=["GET"])
@auth_manager.require_login
def get_seasons():
    """Get all seasons"""
    try:
        user_id = auth_manager.get_current_user_id()
        seasons = job_service.get_all_seasons(user_id)
        return jsonify(
            {"success": True, "data": [season.to_dict() for season in seasons]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons/active", methods=["GET"])
@auth_manager.require_login
def get_active_season():
    """Get the active season"""
    try:
        user_id = auth_manager.get_current_user_id()
        season = job_service.get_active_season(user_id)
        if season:
            stats = job_service.get_job_statistics(user_id)
            return jsonify(
                {"success": True, "data": {"season": season.to_dict(), "stats": stats}}
            )
        else:
            return jsonify({"success": True, "data": None})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons", methods=["POST"])
@auth_manager.require_login
def create_season():
    """Create a new season"""
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        user_id = auth_manager.get_current_user_id()

        if not name:
            return jsonify({"success": False, "error": "Season name is required"}), 400

        success, message, season_id = job_service.create_season(name, user_id)

        if success:
            return jsonify(
                {"success": True, "message": message, "season_id": season_id}
            )
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons/end", methods=["POST"])
@auth_manager.require_login
def end_current_season():
    """End the current active season"""
    try:
        success, message = job_service.end_current_season()

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs", methods=["GET"])
@auth_manager.require_login
def get_jobs():
    """Get all jobs for the active season"""
    try:
        user_id = auth_manager.get_current_user_id()
        season_id = request.args.get("season_id", type=int)
        jobs = job_service.get_jobs_by_season(season_id, user_id)

        return jsonify({"success": True, "data": [job.to_dict() for job in jobs]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs", methods=["POST"])
@auth_manager.require_login
def add_job():
    """Add a new job application"""
    try:
        data = request.get_json()

        # Extract job data
        role = data.get("role", "").strip()
        company_name = data.get("company_name", "").strip()
        source = data.get("source", "").strip() or None
        company_website = data.get("company_website", "").strip() or None
        job_description = data.get("job_description", "").strip() or None
        resume_sent = data.get("resume_sent", "").strip() or None
        status_str = data.get("status", "Applied")
        applied_date_str = data.get("applied_date", "").strip() or None

        # Validate required fields
        if not role:
            return jsonify({"success": False, "error": "Role is required"}), 400
        if not company_name:
            return jsonify({"success": False, "error": "Company name is required"}), 400

        # Convert status string to enum
        try:
            status = JobStatus.from_string(status_str)
        except ValueError:
            return (
                jsonify({"success": False, "error": f"Invalid status: {status_str}"}),
                400,
            )

        user_id = auth_manager.get_current_user_id()
        success, message, job_id = job_service.add_job(
            role=role,
            company_name=company_name,
            source=source,
            company_website=company_website,
            job_description=job_description,
            resume_sent=resume_sent,
            status=status,
            applied_date_str=applied_date_str,
            user_id=user_id,
        )

        if success:
            return jsonify({"success": True, "message": message, "job_id": job_id})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
@auth_manager.require_login
def get_job_details(job_id):
    """Get detailed information for a specific job"""
    try:
        user_id = auth_manager.get_current_user_id()
        job = job_service.get_job_by_id(job_id, user_id)
        if job:
            return jsonify({"success": True, "data": job.to_dict()})
        else:
            return jsonify({"success": False, "error": "Job not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/status", methods=["PUT"])
@auth_manager.require_login
def update_job_status(job_id):
    """Update job application status"""
    try:
        data = request.get_json()
        status_str = data.get("status", "").strip()

        if not status_str:
            return jsonify({"success": False, "error": "Status is required"}), 400

        try:
            status = JobStatus.from_string(status_str)
        except ValueError:
            return (
                jsonify({"success": False, "error": f"Invalid status: {status_str}"}),
                400,
            )

        success, message = job_service.update_job_status(job_id, status)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
@auth_manager.require_login
def delete_job(job_id):
    """Delete a job application"""
    try:
        success, message = job_service.delete_job(job_id)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/search", methods=["GET"])
@auth_manager.require_login
def search_jobs():
    """Search jobs by company name, role, or source"""
    try:
        search_term = request.args.get("q", "").strip()
        if not search_term:
            return jsonify({"success": False, "error": "Search term is required"}), 400

        jobs = job_service.search_jobs(search_term)
        return jsonify({"success": True, "data": [job.to_dict() for job in jobs]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/filter", methods=["GET"])
@auth_manager.require_login
def filter_jobs_by_status():
    """Filter jobs by status"""
    try:
        status_str = request.args.get("status", "").strip()
        if not status_str:
            return jsonify({"success": False, "error": "Status is required"}), 400

        try:
            status = JobStatus.from_string(status_str)
        except ValueError:
            return (
                jsonify({"success": False, "error": f"Invalid status: {status_str}"}),
                400,
            )

        jobs = job_service.get_jobs_by_status(status)
        return jsonify({"success": True, "data": [job.to_dict() for job in jobs]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/statistics", methods=["GET"])
@auth_manager.require_login
def get_statistics():
    """Get job application statistics"""
    try:
        stats = job_service.get_job_statistics()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/job-statuses", methods=["GET"])
@auth_manager.require_login
def get_job_statuses():
    """Get all available job statuses"""
    try:
        statuses = JobStatus.get_all_statuses()
        return jsonify({"success": True, "data": statuses})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def check_database():
    """Check if database is properly set up"""
    try:
        from job_tracker.database import DatabaseConnection

        db = DatabaseConnection()

        # Check if users table exists
        result = db.execute_single_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )

        if not result:
            print("⚠️  Users table not found. Please run: python migrate_db.py")
            return False

        print("✅ Database tables found")
        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        print("💡 Try running: python migrate_db.py")
        return False


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

    migrate_database()

    print("🚀 Starting Job Application Tracker Web Server...")

    # Check database setup
    if not check_database():
        print("❌ Database setup incomplete. Exiting...")
        exit(1)

    # Get configuration from environment
    port = int(os.getenv("PORT", 5050))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_ENV") != "production"

    print(f"📊 Dashboard available at: http://localhost:{port}")
    print("🔧 API documentation at: http://localhost:{port}/api")
    print("💡 Press Ctrl+C to stop the server")

    try:
        app.run(debug=debug, host=host, port=port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
