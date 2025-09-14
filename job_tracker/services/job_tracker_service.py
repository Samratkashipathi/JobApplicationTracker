"""
Job Tracker Service - Business logic layer
"""

from typing import List, Optional, Dict
from ..database import DatabaseConnection, JobRepository, SeasonRepository
from ..models import Job, Season, JobStatus
from ..utils.validation import (
    validate_season_name,
    validate_company_name,
    validate_role,
)
from ..config import DEFAULT_DB_PATH


class JobTrackerService:
    """Main service class for job tracking operations"""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_connection = DatabaseConnection(db_path)
        self.season_repo = SeasonRepository(self.db_connection)
        self.job_repo = JobRepository(self.db_connection)

    # Season Management
    def create_season(
        self, name: str, user_id: int = None
    ) -> tuple[bool, str, Optional[int]]:
        """
        Create a new season
        Returns (success, message, season_id)
        """
        # Validate input
        is_valid, error = validate_season_name(name)
        if not is_valid:
            return False, error, None

        try:
            season = Season(name=name)
            season_id = self.season_repo.create(season, user_id)
            return True, f"Season '{name}' created successfully!", season_id
        except Exception as e:
            return False, f"Failed to create season: {str(e)}", None

    def end_current_season(self) -> tuple[bool, str]:
        """
        End the current active season
        Returns (success, message)
        """
        try:
            active_season = self.season_repo.get_active()
            if not active_season:
                return False, "No active season found"

            if self.season_repo.end_current():
                return True, f"Season '{active_season.name}' ended successfully"
            else:
                return False, "Failed to end season"
        except Exception as e:
            return False, f"Error ending season: {str(e)}"

    def get_active_season(self, user_id: int = None) -> Optional[Season]:
        """Get the currently active season"""
        return self.season_repo.get_active(user_id)

    def get_all_seasons(self, user_id: int = None) -> List[Season]:
        """Get all seasons"""
        return self.season_repo.get_all(user_id)

    # Job Management
    def add_job(
        self,
        role: str,
        company_name: str,
        source: str = None,
        company_website: str = None,
        job_description: str = None,
        resume_sent: str = None,
        status: JobStatus = JobStatus.APPLIED,
        applied_date_str: str = None,
        user_id: int = None,
    ) -> tuple[bool, str, Optional[int]]:
        """
        Add a new job application
        Returns (success, message, job_id)
        """
        # Validate inputs
        is_valid, error = validate_role(role)
        if not is_valid:
            return False, f"Invalid role: {error}", None

        is_valid, error = validate_company_name(company_name)
        if not is_valid:
            return False, f"Invalid company name: {error}", None

        # Check if there's an active season
        active_season = self.season_repo.get_active(user_id)
        if not active_season:
            return False, "No active season found. Please create a season first.", None

        try:
            # Parse applied date if provided
            applied_date = None
            if applied_date_str:
                from ..utils.date_utils import parse_date

                try:
                    applied_date = parse_date(applied_date_str)
                except ValueError as e:
                    return False, f"Invalid applied date: {str(e)}", None

            job = Job(
                season_id=active_season.id,
                role=role,
                company_name=company_name,
                source=source,
                company_website=company_website,
                job_description=job_description,
                resume_sent=resume_sent,
                current_status=status,
                applied_date=applied_date,
            )

            job_id = self.job_repo.create(job, user_id)
            return (
                True,
                f"Job application for {role} at {company_name} added successfully!",
                job_id,
            )
        except Exception as e:
            return False, f"Failed to add job: {str(e)}", None

    def update_job_status(self, job_id: int, new_status: JobStatus) -> tuple[bool, str]:
        """
        Update job application status
        Returns (success, message)
        """
        try:
            # Verify job exists
            job = self.job_repo.get_by_id(job_id)
            if not job:
                return False, "Job not found"

            if self.job_repo.update_status(job_id, new_status):
                return True, f"Job status updated to '{new_status.value}'"
            else:
                return False, "Failed to update job status"
        except Exception as e:
            return False, f"Error updating job: {str(e)}"

    def get_job_by_id(self, job_id: int, user_id: int = None) -> Optional[Job]:
        """Get a specific job by ID"""
        return self.job_repo.get_by_id(job_id, user_id)

    def get_jobs_by_season(
        self, season_id: int = None, user_id: int = None
    ) -> List[Job]:
        """Get all jobs for a season (defaults to active season)"""
        if season_id is None:
            active_season = self.season_repo.get_active(user_id)
            if not active_season:
                return []
            season_id = active_season.id

        return self.job_repo.get_by_season(season_id, user_id)

    def get_all_jobs(self) -> List[Job]:
        """Get all jobs across all seasons"""
        return self.job_repo.get_all()

    def get_jobs_by_status(self, status: JobStatus, season_id: int = None) -> List[Job]:
        """Get jobs filtered by status"""
        if season_id is None:
            active_season = self.season_repo.get_active()
            if not active_season:
                return []
            season_id = active_season.id

        return self.job_repo.get_by_status(status, season_id)

    def search_jobs(self, search_term: str, season_id: int = None) -> List[Job]:
        """Search jobs by company name, role, or source"""
        if season_id is None:
            active_season = self.season_repo.get_active()
            if not active_season:
                return []
            season_id = active_season.id

        return self.job_repo.search(search_term, season_id)

    def get_job_statistics(self, season_id: int = None) -> Dict:
        """Get statistics for jobs in a season"""
        if season_id is None:
            active_season = self.season_repo.get_active()
            if not active_season:
                return {}
            season_id = active_season.id

        return self.job_repo.get_statistics(season_id)

    def delete_job(self, job_id: int) -> tuple[bool, str]:
        """
        Delete a job application
        Returns (success, message)
        """
        try:
            # Verify job exists
            job = self.job_repo.get_by_id(job_id)
            if not job:
                return False, "Job not found"

            if self.job_repo.delete(job_id):
                return (
                    True,
                    f"Job application for {job.role} at {job.company_name} deleted successfully",
                )
            else:
                return False, "Failed to delete job"
        except Exception as e:
            return False, f"Error deleting job: {str(e)}"

    def update_job(self, job: Job) -> tuple[bool, str]:
        """
        Update a job application
        Returns (success, message)
        """
        try:
            # Validate inputs
            is_valid, error = validate_role(job.role)
            if not is_valid:
                return False, f"Invalid role: {error}"

            is_valid, error = validate_company_name(job.company_name)
            if not is_valid:
                return False, f"Invalid company name: {error}"

            if self.job_repo.update(job):
                return (
                    True,
                    f"Job application for {job.role} at {job.company_name} updated successfully",
                )
            else:
                return False, "Failed to update job"
        except Exception as e:
            return False, f"Error updating job: {str(e)}"
