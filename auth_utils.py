"""
Authentication utilities for Job Application Tracker
"""

import re
from functools import wraps
from flask import session, request, jsonify, redirect, url_for
from job_tracker.database import DatabaseConnection, UserRepository
from job_tracker.models.user import User


class AuthManager:
    """Handles user authentication and session management"""

    def __init__(self):
        self.db = DatabaseConnection()
        self.user_repo = UserRepository(self.db)

    def register_user(
        self, username: str, email: str, password: str, full_name: str
    ) -> tuple[bool, str, User]:
        """Register a new user"""
        # Validation
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long", None

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return (
                False,
                "Username can only contain letters, numbers, and underscores",
                None,
            )

        if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return False, "Please enter a valid email address", None

        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long", None

        if not full_name or len(full_name.strip()) < 2:
            return False, "Full name must be at least 2 characters long", None

        # Check if username or email already exists
        if self.user_repo.username_exists(username):
            return False, "Username already exists", None

        if self.user_repo.email_exists(email):
            return False, "Email already exists", None

        try:
            # Create user
            user = User(
                username=username.lower().strip(),
                email=email.lower().strip(),
                full_name=full_name.strip(),
            )
            user.set_password(password)

            user_id = self.user_repo.create(user)
            user.id = user_id

            return True, "User registered successfully", user

        except ValueError as e:
            # Handle user-friendly errors from UserRepository
            return False, str(e), None
        except Exception as e:
            error_str = str(e).lower()
            if "unique constraint failed: users.username" in error_str:
                return False, "Username already exists", None
            elif "unique constraint failed: users.email" in error_str:
                return False, "Email already exists", None
            elif "unique constraint" in error_str:
                return False, "Username or email already exists", None
            else:
                return False, f"Registration failed: {str(e)}", None

    def login_user(self, username: str, password: str) -> tuple[bool, str, User]:
        """Login user with username/email and password"""
        if not username or not password:
            return False, "Username and password are required", None

        # Try to find user by username or email
        user = self.user_repo.get_by_username(username.lower().strip())
        if not user:
            user = self.user_repo.get_by_email(username.lower().strip())

        if not user:
            return False, "Invalid username/email or password", None

        if not user.check_password(password):
            return False, "Invalid username/email or password", None

        # Update last login
        self.user_repo.update_last_login(user.id)
        user.update_last_login()

        # Store user in session (only if we're in a Flask request context)
        try:
            session["user_id"] = user.id
            session["username"] = user.username
            session.permanent = True
        except RuntimeError:
            # Not in a request context (e.g., during testing)
            pass

        return True, "Login successful", user

    def logout_user(self):
        """Logout current user"""
        try:
            session.pop("user_id", None)
            session.pop("username", None)
        except RuntimeError:
            # Not in a request context (e.g., during testing)
            pass

    def get_current_user(self) -> User:
        """Get current logged-in user"""
        try:
            user_id = session.get("user_id")
            print(f"🔍 get_current_user: user_id from session = {user_id}")
            if user_id:
                user = self.user_repo.get_by_id(user_id)
                print(
                    f"🔍 get_current_user: user from DB = {user.username if user else None}"
                )
                return user
        except RuntimeError:
            # Not in a request context (e.g., during testing)
            print("🔍 get_current_user: Not in request context")
            pass
        except Exception as e:
            print(f"❌ get_current_user error: {e}")
        return None

    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        try:
            user_id = session.get("user_id")
            has_user_id = "user_id" in session and session["user_id"] is not None
            print(f"🔍 is_logged_in: user_id = {user_id}, has_user_id = {has_user_id}")
            return has_user_id
        except RuntimeError:
            # Not in a request context (e.g., during testing)
            print("🔍 is_logged_in: Not in request context")
            return False

    def get_current_user_id(self) -> int:
        """Get current user ID"""
        try:
            return session.get("user_id")
        except RuntimeError:
            # Not in a request context (e.g., during testing)
            return None

    def require_login(self, f):
        """Decorator to require login for routes"""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_logged_in():
                if request.is_json:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Authentication required",
                                "login_required": True,
                            }
                        ),
                        401,
                    )
                return redirect(url_for("login_page"))
            return f(*args, **kwargs)

        return decorated_function


# Global auth manager instance
auth_manager = AuthManager()
