"""
Repository classes for database operations
"""

from datetime import datetime
from typing import List, Optional
from .connection import DatabaseConnection
from ..models import Season, Job, JobStatus


class SeasonRepository:
    """Repository for Season database operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create(self, season: Season) -> int:
        """Create a new season"""
        # First, deactivate all existing seasons
        self.db.execute_command(
            "UPDATE seasons SET is_active = 0, end_date = ? WHERE is_active = 1",
            (datetime.now().isoformat(),)
        )
        
        # Create new active season
        season_id = self.db.execute_command(
            """
            INSERT INTO seasons (name, start_date, is_active) 
            VALUES (?, ?, 1)
            """,
            (season.name, season.start_date.isoformat())
        )
        
        season.id = season_id
        return season_id
    
    def get_active(self) -> Optional[Season]:
        """Get the currently active season"""
        data = self.db.execute_single_query(
            "SELECT * FROM seasons WHERE is_active = 1"
        )
        return Season.from_dict(data) if data else None
    
    def get_by_id(self, season_id: int) -> Optional[Season]:
        """Get season by ID"""
        data = self.db.execute_single_query(
            "SELECT * FROM seasons WHERE id = ?",
            (season_id,)
        )
        return Season.from_dict(data) if data else None
    
    def get_all(self) -> List[Season]:
        """Get all seasons"""
        data = self.db.execute_query(
            "SELECT * FROM seasons ORDER BY created_at DESC"
        )
        return [Season.from_dict(row) for row in data]
    
    def end_current(self) -> bool:
        """End the current active season"""
        rows_affected = self.db.execute_command(
            """
            UPDATE seasons 
            SET is_active = 0, end_date = ? 
            WHERE is_active = 1
            """,
            (datetime.now().isoformat(),)
        )
        return rows_affected > 0
    
    def update(self, season: Season) -> bool:
        """Update an existing season"""
        if not season.id:
            return False
        
        rows_affected = self.db.execute_command(
            """
            UPDATE seasons 
            SET name = ?, start_date = ?, end_date = ?, is_active = ?
            WHERE id = ?
            """,
            (
                season.name,
                season.start_date.isoformat() if season.start_date else None,
                season.end_date.isoformat() if season.end_date else None,
                1 if season.is_active else 0,
                season.id
            )
        )
        return rows_affected > 0
    
    def delete(self, season_id: int) -> bool:
        """Delete a season and all its jobs"""
        rows_affected = self.db.execute_command(
            "DELETE FROM seasons WHERE id = ?",
            (season_id,)
        )
        return rows_affected > 0


class JobRepository:
    """Repository for Job database operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create(self, job: Job) -> int:
        """Create a new job application"""
        job_id = self.db.execute_command(
            """
            INSERT INTO jobs (season_id, role, company_name, company_website, 
                            source, current_status, job_description, resume_sent,
                            applied_date, last_updated) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.season_id,
                job.role,
                job.company_name,
                job.company_website,
                job.source,
                job.current_status.value,
                job.job_description,
                job.resume_sent,
                job.applied_date.isoformat() if job.applied_date else None,
                job.last_updated.isoformat() if job.last_updated else None,
            )
        )
        
        job.id = job_id
        return job_id
    
    def get_by_id(self, job_id: int) -> Optional[Job]:
        """Get a specific job by ID"""
        data = self.db.execute_single_query(
            """
            SELECT j.*, s.name as season_name 
            FROM jobs j 
            JOIN seasons s ON j.season_id = s.id 
            WHERE j.id = ?
            """,
            (job_id,)
        )
        return Job.from_dict(data) if data else None
    
    def get_by_season(self, season_id: int) -> List[Job]:
        """Get all jobs for a specific season"""
        data = self.db.execute_query(
            """
            SELECT j.*, s.name as season_name 
            FROM jobs j 
            JOIN seasons s ON j.season_id = s.id 
            WHERE j.season_id = ? 
            ORDER BY j.applied_date DESC
            """,
            (season_id,)
        )
        return [Job.from_dict(row) for row in data]
    
    def get_all(self) -> List[Job]:
        """Get all jobs across all seasons"""
        data = self.db.execute_query(
            """
            SELECT j.*, s.name as season_name 
            FROM jobs j 
            JOIN seasons s ON j.season_id = s.id 
            ORDER BY j.applied_date DESC
            """
        )
        return [Job.from_dict(row) for row in data]
    
    def get_by_status(self, status: JobStatus, season_id: int = None) -> List[Job]:
        """Get jobs filtered by status"""
        if season_id:
            data = self.db.execute_query(
                """
                SELECT j.*, s.name as season_name 
                FROM jobs j 
                JOIN seasons s ON j.season_id = s.id 
                WHERE j.current_status = ? AND j.season_id = ?
                ORDER BY j.applied_date DESC
                """,
                (status.value, season_id)
            )
        else:
            data = self.db.execute_query(
                """
                SELECT j.*, s.name as season_name 
                FROM jobs j 
                JOIN seasons s ON j.season_id = s.id 
                WHERE j.current_status = ?
                ORDER BY j.applied_date DESC
                """,
                (status.value,)
            )
        
        return [Job.from_dict(row) for row in data]
    
    def search(self, search_term: str, season_id: int = None) -> List[Job]:
        """Search jobs by company name, role, or source"""
        search_pattern = f"%{search_term}%"
        
        if season_id:
            data = self.db.execute_query(
                """
                SELECT j.*, s.name as season_name 
                FROM jobs j 
                JOIN seasons s ON j.season_id = s.id 
                WHERE j.season_id = ? AND (
                    j.company_name LIKE ? OR 
                    j.role LIKE ? OR 
                    j.source LIKE ?
                )
                ORDER BY j.applied_date DESC
                """,
                (season_id, search_pattern, search_pattern, search_pattern)
            )
        else:
            data = self.db.execute_query(
                """
                SELECT j.*, s.name as season_name 
                FROM jobs j 
                JOIN seasons s ON j.season_id = s.id 
                WHERE j.company_name LIKE ? OR 
                      j.role LIKE ? OR 
                      j.source LIKE ?
                ORDER BY j.applied_date DESC
                """,
                (search_pattern, search_pattern, search_pattern)
            )
        
        return [Job.from_dict(row) for row in data]
    
    def update_status(self, job_id: int, new_status: JobStatus) -> bool:
        """Update job application status"""
        rows_affected = self.db.execute_command(
            """
            UPDATE jobs 
            SET current_status = ?, last_updated = ? 
            WHERE id = ?
            """,
            (new_status.value, datetime.now().isoformat(), job_id)
        )
        return rows_affected > 0
    
    def update(self, job: Job) -> bool:
        """Update an existing job"""
        if not job.id:
            return False
        
        rows_affected = self.db.execute_command(
            """
            UPDATE jobs 
            SET role = ?, company_name = ?, company_website = ?, source = ?,
                current_status = ?, job_description = ?, resume_sent = ?,
                last_updated = ?
            WHERE id = ?
            """,
            (
                job.role,
                job.company_name,
                job.company_website,
                job.source,
                job.current_status.value,
                job.job_description,
                job.resume_sent,
                datetime.now().isoformat(),
                job.id
            )
        )
        return rows_affected > 0
    
    def delete(self, job_id: int) -> bool:
        """Delete a job application"""
        rows_affected = self.db.execute_command(
            "DELETE FROM jobs WHERE id = ?",
            (job_id,)
        )
        return rows_affected > 0
    
    def get_statistics(self, season_id: int) -> dict:
        """Get statistics for jobs in a season"""
        # Total jobs
        total_data = self.db.execute_single_query(
            "SELECT COUNT(*) as total FROM jobs WHERE season_id = ?",
            (season_id,)
        )
        total = total_data["total"] if total_data else 0
        
        # Jobs by status
        status_data = self.db.execute_query(
            """
            SELECT current_status, COUNT(*) as count 
            FROM jobs 
            WHERE season_id = ? 
            GROUP BY current_status
            """,
            (season_id,)
        )
        
        status_counts = {row["current_status"]: row["count"] for row in status_data}
        
        return {
            "total_jobs": total,
            "status_breakdown": status_counts
        }
