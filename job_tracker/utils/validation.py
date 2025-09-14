"""
Validation utilities for Job Tracker
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_input(value: str, required: bool = True, min_length: int = 0, max_length: int = None) -> tuple[bool, str]:
    """
    Validate input string
    Returns (is_valid, error_message)
    """
    if not value or not value.strip():
        if required:
            return False, "This field is required"
        return True, ""
    
    value = value.strip()
    
    if len(value) < min_length:
        return False, f"Minimum length is {min_length} characters"
    
    if max_length and len(value) > max_length:
        return False, f"Maximum length is {max_length} characters"
    
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    if not email:
        return True, ""  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    return False, "Invalid email format"


def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL format"""
    if not url:
        return True, ""  # URL is optional
    
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True, ""
        return False, "Invalid URL format"
    except Exception:
        return False, "Invalid URL format"


def validate_season_name(name: str) -> tuple[bool, str]:
    """Validate season name"""
    is_valid, error = validate_input(name, required=True, min_length=3, max_length=100)
    if not is_valid:
        return is_valid, error
    
    # Check for special characters that might cause issues
    if any(char in name for char in ['<', '>', '"', "'"]):
        return False, "Season name cannot contain special characters: < > \" '"
    
    return True, ""


def validate_company_name(name: str) -> tuple[bool, str]:
    """Validate company name"""
    return validate_input(name, required=True, min_length=2, max_length=200)


def validate_role(role: str) -> tuple[bool, str]:
    """Validate job role"""
    return validate_input(role, required=True, min_length=2, max_length=200)


def sanitize_input(value: str) -> str:
    """Sanitize input by removing potentially harmful characters"""
    if not value:
        return ""
    
    # Remove control characters and excessive whitespace
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', value)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def truncate_text(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """Truncate text for display purposes"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
