"""
Command Line Interface for Job Tracker
"""

from typing import Optional
from ..services import JobTrackerService
from ..models import JobStatus
from .display import DisplayManager


class JobTrackerCLI:
    """Command Line Interface for Job Application Tracker"""

    def __init__(self, db_path: str = None):
        self.service = JobTrackerService(db_path) if db_path else JobTrackerService()
        self.display = DisplayManager()
        self.job_statuses = JobStatus.get_all_statuses()

    def create_season(self):
        """Create a new job hunting season"""
        self.display.print_header("Create New Season")

        # Check if there's an active season
        active_season = self.service.get_active_season()
        if active_season:
            self.display.print_warning(f"Current active season: {active_season.name}")
            if not self.display.confirm_action(
                "Creating a new season will end the current one. Continue?"
            ):
                return

        name = self.display.get_input(
            "Enter season name (e.g., 'Sept 2024', 'Career Change 2024'): "
        )

        success, message, season_id = self.service.create_season(name)
        if success:
            self.display.print_success(message)
        else:
            self.display.print_error(message)

    def end_current_season(self):
        """End the current active season"""
        self.display.print_header("End Current Season")

        active_season = self.service.get_active_season()
        if not active_season:
            self.display.print_warning("No active season found")
            return

        self.display.print_info(f"Current active season: {active_season.name}")
        self.display.print_info(f"Started: {active_season.start_date}")

        if self.display.confirm_action("Are you sure you want to end this season?"):
            success, message = self.service.end_current_season()
            if success:
                self.display.print_success(message)
            else:
                self.display.print_error(message)

    def view_seasons(self):
        """View all seasons"""
        seasons = self.service.get_all_seasons()
        self.display.display_seasons_table(seasons)

    def add_job(self):
        """Add a new job application"""
        self.display.print_header("Add New Job Application")

        # Check if there's an active season
        active_season = self.service.get_active_season()
        if not active_season:
            self.display.print_error(
                "No active season found. Please create a season first."
            )
            return

        self.display.print_info(f"Adding job to season: {active_season.name}")

        # Get job details
        role = self.display.get_input("Role/Position: ")
        company_name = self.display.get_input("Company Name: ")
        source = self.display.get_input(
            "Source (e.g., LinkedIn, Company Website, Referral): ", required=False
        )
        company_website = self.display.get_input("Company Website: ", required=False)

        # Get initial status
        status_str = self.display.get_choice("Initial Status: ", self.job_statuses)
        status = JobStatus.from_string(status_str)

        job_description = self.display.get_input(
            "Job Description (brief): ", required=False
        )
        resume_sent = self.display.get_input(
            "Resume Sent (Google drive link): ", required=False
        )

        # Get applied date
        applied_date_str = self.display.get_date_input("Applied Date", required=False)

        success, message, job_id = self.service.add_job(
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
            self.display.print_success(message)
        else:
            self.display.print_error(message)

    def update_job_status(self):
        """Update job application status"""
        self.display.print_header("Update Job Status")

        # First, show current jobs
        jobs = self.service.get_jobs_by_season()
        if not jobs:
            self.display.print_warning("No jobs found in current season")
            return

        # Display current jobs
        self.display.display_jobs_table(jobs, "Current Jobs")

        # Get job ID to update
        try:
            job_id = int(self.display.get_input("Enter Job ID to update: "))
        except ValueError:
            self.display.print_error("Invalid job ID")
            return

        # Verify job exists
        job = self.service.get_job_by_id(job_id)
        if not job:
            self.display.print_error("Job not found")
            return

        self.display.print_info(f"Current job: {job.role} at {job.company_name}")
        self.display.print_info(f"Current status: {job.current_status.value}")

        # Get new status
        new_status_str = self.display.get_choice("New Status: ", self.job_statuses)
        new_status = JobStatus.from_string(new_status_str)

        success, message = self.service.update_job_status(job_id, new_status)
        if success:
            self.display.print_success(message)
        else:
            self.display.print_error(message)

    def view_jobs(self):
        """View all jobs in current season"""
        active_season = self.service.get_active_season()
        if not active_season:
            self.display.print_error("No active season found")
            return

        jobs = self.service.get_jobs_by_season()
        title = f"Job Applications - {active_season.name}"
        self.display.display_jobs_table(jobs, title)

    def view_job_details(self):
        """View detailed information for a specific job"""
        try:
            job_id = int(self.display.get_input("Enter Job ID: "))
        except ValueError:
            self.display.print_error("Invalid job ID")
            return

        job = self.service.get_job_by_id(job_id)
        if not job:
            self.display.print_error("Job not found")
            return

        self.display.display_job_details(job)

    def view_statistics(self):
        """View job application statistics"""
        active_season = self.service.get_active_season()
        if not active_season:
            self.display.print_error("No active season found")
            return

        stats = self.service.get_job_statistics()
        self.display.display_statistics(active_season, stats)

    def search_jobs(self):
        """Search jobs by company name or role"""
        self.display.print_header("Search Jobs")

        search_term = self.display.get_input(
            "Enter search term (company name, role, or source): "
        )
        jobs = self.service.search_jobs(search_term)

        if not jobs:
            self.display.print_warning(f"No jobs found matching '{search_term}'")
            return

        title = f"Search Results for '{search_term}'"
        self.display.display_jobs_table(jobs, title)

    def filter_by_status(self):
        """Filter jobs by status"""
        self.display.print_header("Filter Jobs by Status")

        status_str = self.display.get_choice(
            "Select status to filter by: ", self.job_statuses
        )
        status = JobStatus.from_string(status_str)

        jobs = self.service.get_jobs_by_status(status)
        if not jobs:
            self.display.print_warning(f"No jobs found with status '{status.value}'")
            return

        title = f"Jobs with status '{status.value}'"
        self.display.display_jobs_table(jobs, title)

    def run(self):
        """Main application loop"""
        self.display.print_menu_header()

        while True:
            try:
                # Display current season info
                active_season = self.service.get_active_season()
                if active_season:
                    stats = self.service.get_job_statistics()
                    self.display.display_season_info(active_season, stats)
                else:
                    self.display.display_no_season_warning()

                # Display main menu
                self.display.print_main_menu()

                choice = self.display.get_input("\nEnter your choice (0-11): ").strip()

                if choice == "0":
                    self.display.print_success(
                        "Thank you for using Job Application Tracker!"
                    )
                    self.display.print_success("Good luck with your job search! 🚀")
                    break
                elif choice == "1":
                    self.create_season()
                    self.display.pause()
                elif choice == "2":
                    self.end_current_season()
                    self.display.pause()
                elif choice == "3":
                    self.view_seasons()
                    self.display.pause()
                elif choice == "4":
                    self.add_job()
                    self.display.pause()
                elif choice == "5":
                    self.update_job_status()
                    self.display.pause()
                elif choice == "6":
                    self.view_jobs()
                    self.display.pause()
                elif choice == "7":
                    self.view_job_details()
                    self.display.pause()
                elif choice == "8":
                    self.view_statistics()
                    self.display.pause()
                elif choice == "9":
                    self.search_jobs()
                    self.display.pause()
                elif choice == "10":
                    self.filter_by_status()
                    self.display.pause()
                elif choice == "11":
                    self.display.clear_screen()
                else:
                    self.display.print_error(
                        "Invalid choice. Please enter a number between 0-11."
                    )
                    self.display.pause()

            except KeyboardInterrupt:
                self.display.print_warning("\n\nGoodbye! 👋")
                break
            except Exception as e:
                self.display.print_error(f"An unexpected error occurred: {str(e)}")
                self.display.pause()
