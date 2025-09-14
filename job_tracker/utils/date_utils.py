"""
Date utilities for Job Tracker
"""

from datetime import datetime
from typing import Optional


def format_date(date: Optional[datetime], format_str: str = "%Y-%m-%d") -> str:
    """Format a datetime object to string"""
    if date is None:
        return "N/A"
    return date.strftime(format_str)


def format_datetime(date: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format a datetime object to string with time"""
    if date is None:
        return "N/A"
    return date.strftime(format_str)


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string to datetime object"""
    if not date_str or date_str == "N/A":
        return None
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Try common date formats
        formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")


def days_between(start_date: Optional[datetime], end_date: Optional[datetime] = None) -> int:
    """Calculate days between two dates"""
    if start_date is None:
        return 0
    
    if end_date is None:
        end_date = datetime.now()
    
    return (end_date - start_date).days


def format_duration(days: int) -> str:
    """Format duration in days to human readable string"""
    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day ago"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
