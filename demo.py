#!/usr/bin/env python3
"""
Demo script to populate the job tracker with sample data
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.services import JobTrackerService
from job_tracker.models import JobStatus


def create_demo_data():
    """Create sample data for demonstration"""
    service = JobTrackerService()

    # Create a demo season
    print("Creating demo season...")
    success, message, season_id = service.create_season("Demo Season - Fall 2024")
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        return

    # Sample job applications
    demo_jobs = [
        {
            "role": "Senior Software Engineer",
            "company_name": "Google",
            "source": "LinkedIn",
            "company_website": "https://google.com",
            "job_description": "Full-stack development with focus on scalable systems",
            "status": JobStatus.TECHNICAL_INTERVIEW,
            "days_ago": 5,
        },
        {
            "role": "Frontend Developer",
            "company_name": "Netflix",
            "source": "Company Website",
            "company_website": "https://netflix.com",
            "job_description": "React and TypeScript development for streaming platform",
            "status": JobStatus.PHONE_SCREEN,
            "days_ago": 10,
        },
        {
            "role": "DevOps Engineer",
            "company_name": "Amazon",
            "source": "Referral",
            "company_website": "https://amazon.com",
            "job_description": "AWS infrastructure and CI/CD pipeline management",
            "status": JobStatus.APPLIED,
            "days_ago": 3,
        },
        {
            "role": "Data Scientist",
            "company_name": "Microsoft",
            "source": "Indeed",
            "company_website": "https://microsoft.com",
            "job_description": "Machine learning and data analysis for Azure services",
            "status": JobStatus.FINAL_INTERVIEW,
            "days_ago": 15,
        },
        {
            "role": "Full Stack Developer",
            "company_name": "Spotify",
            "source": "AngelList",
            "company_website": "https://spotify.com",
            "job_description": "Music streaming platform development",
            "status": JobStatus.OFFER,
            "days_ago": 20,
        },
        {
            "role": "Backend Engineer",
            "company_name": "Uber",
            "source": "Glassdoor",
            "company_website": "https://uber.com",
            "job_description": "Microservices architecture for ride-sharing platform",
            "status": JobStatus.REJECTED,
            "days_ago": 25,
        },
        {
            "role": "Software Engineer",
            "company_name": "Apple",
            "source": "Company Website",
            "company_website": "https://apple.com",
            "job_description": "iOS app development and system integration",
            "status": JobStatus.ONSITE_INTERVIEW,
            "days_ago": 7,
        },
        {
            "role": "Cloud Engineer",
            "company_name": "Salesforce",
            "source": "LinkedIn",
            "company_website": "https://salesforce.com",
            "job_description": "Cloud infrastructure and platform development",
            "status": JobStatus.APPLIED,
            "days_ago": 2,
        },
    ]

    print(f"\nAdding {len(demo_jobs)} demo job applications...")

    for job_data in demo_jobs:
        # Calculate applied date
        applied_date = datetime.now() - timedelta(days=job_data["days_ago"])
        applied_date_str = applied_date.strftime("%Y-%m-%d")

        success, message, job_id = service.add_job(
            role=job_data["role"],
            company_name=job_data["company_name"],
            source=job_data["source"],
            company_website=job_data["company_website"],
            job_description=job_data["job_description"],
            status=job_data["status"],
            applied_date_str=applied_date_str,
        )

        if success:
            print(f"✅ Added: {job_data['role']} at {job_data['company_name']}")
        else:
            print(
                f"❌ Failed to add: {job_data['role']} at {job_data['company_name']} - {message}"
            )

    # Display statistics
    print("\n📊 Demo Data Statistics:")
    stats = service.get_job_statistics()
    print(f"Total Applications: {stats.get('total', 0)}")
    print(f"Active Applications: {stats.get('active', 0)}")
    print(f"Interviews: {stats.get('interviews', 0)}")
    print(f"Offers: {stats.get('offers', 0)}")

    print("\n🚀 Demo data created successfully!")
    print("You can now run the web interface with: python app.py")
    print("Or the CLI with: python main.py")


if __name__ == "__main__":
    create_demo_data()
