#!/usr/bin/env python3
"""
Job Application Tracker - Web Application
A beautiful web interface for tracking job applications across different seasons.
"""

import sys
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

# Add the current directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.services import JobTrackerService
from job_tracker.models import JobStatus

app = Flask(__name__)
CORS(app)

# Initialize the job tracker service
job_service = JobTrackerService()


@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("index.html")


@app.route("/api/seasons", methods=["GET"])
def get_seasons():
    """Get all seasons"""
    try:
        seasons = job_service.get_all_seasons()
        return jsonify(
            {"success": True, "data": [season.to_dict() for season in seasons]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons/active", methods=["GET"])
def get_active_season():
    """Get the active season"""
    try:
        season = job_service.get_active_season()
        if season:
            stats = job_service.get_job_statistics()
            return jsonify(
                {"success": True, "data": {"season": season.to_dict(), "stats": stats}}
            )
        else:
            return jsonify({"success": True, "data": None})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons", methods=["POST"])
def create_season():
    """Create a new season"""
    try:
        data = request.get_json()
        name = data.get("name", "").strip()

        if not name:
            return jsonify({"success": False, "error": "Season name is required"}), 400

        success, message, season_id = job_service.create_season(name)

        if success:
            return jsonify(
                {"success": True, "message": message, "season_id": season_id}
            )
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/seasons/end", methods=["POST"])
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
def get_jobs():
    """Get all jobs for the active season"""
    try:
        season_id = request.args.get("season_id", type=int)
        jobs = job_service.get_jobs_by_season(season_id)

        return jsonify({"success": True, "data": [job.to_dict() for job in jobs]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs", methods=["POST"])
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

        success, message, job_id = job_service.add_job(
            role=role,
            company_name=company_name,
            source=source,
            company_website=company_website,
            job_description=job_description,
            resume_sent=resume_sent,
            status=status,
            applied_date_str=applied_date_str,
        )

        if success:
            return jsonify({"success": True, "message": message, "job_id": job_id})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job_details(job_id):
    """Get detailed information for a specific job"""
    try:
        job = job_service.get_job_by_id(job_id)
        if job:
            return jsonify({"success": True, "data": job.to_dict()})
        else:
            return jsonify({"success": False, "error": "Job not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/status", methods=["PUT"])
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
def get_statistics():
    """Get job application statistics"""
    try:
        stats = job_service.get_job_statistics()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/job-statuses", methods=["GET"])
def get_job_statuses():
    """Get all available job statuses"""
    try:
        statuses = JobStatus.get_all_statuses()
        return jsonify({"success": True, "data": statuses})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

    print("🚀 Starting Job Application Tracker Web Server...")
    print("📊 Dashboard available at: http://localhost:5050")
    print("🔧 API documentation at: http://localhost:5050/api")

    app.run(debug=True, host="0.0.0.0", port=5050)
