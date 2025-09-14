#!/usr/bin/env python3
"""
Test script for authentication system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth_utils import auth_manager


def test_registration():
    """Test user registration"""
    print("Testing user registration...")

    # Test user data
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    full_name = "Test User"

    success, message, user = auth_manager.register_user(
        username, email, password, full_name
    )

    if success:
        print(f"✅ Registration successful: {message}")
        print(f"   User ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.full_name}")
        return user
    else:
        print(f"❌ Registration failed: {message}")
        return None


def test_login(username, password):
    """Test user login"""
    print(f"\nTesting login for {username}...")

    success, message, user = auth_manager.login_user(username, password)

    if success:
        print(f"✅ Login successful: {message}")
        print(f"   User ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        return user
    else:
        print(f"❌ Login failed: {message}")
        return None


def main():
    """Main test function"""
    print("🔐 Testing Job Tracker Authentication System\n")

    # Test registration
    user = test_registration()

    if user:
        # Test login
        login_user = test_login(user.username, "testpass123")

        if login_user:
            print(f"\n🎉 Authentication system is working correctly!")
        else:
            print(f"\n❌ Login test failed")
    else:
        print(f"\n❌ Registration test failed")


if __name__ == "__main__":
    main()
