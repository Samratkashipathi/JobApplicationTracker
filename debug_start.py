#!/usr/bin/env python3
"""
Debug startup script for Job Application Tracker
Helps identify infinite loop issues
"""

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_imports():
    """Test all imports to identify issues"""
    print("🔍 Testing imports...")
    
    try:
        print("  - Testing job_tracker imports...")
        from job_tracker.services import JobTrackerService
        from job_tracker.models import JobStatus
        print("  ✅ job_tracker imports successful")
    except Exception as e:
        print(f"  ❌ job_tracker import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("  - Testing auth_utils import...")
        from auth_utils import auth_manager
        print("  ✅ auth_utils import successful")
    except Exception as e:
        print(f"  ❌ auth_utils import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("  - Testing Flask imports...")
        from flask import Flask, render_template, request, jsonify, redirect, url_for, session
        from flask_cors import CORS
        from flask_session import Session
        print("  ✅ Flask imports successful")
    except Exception as e:
        print(f"  ❌ Flask import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def debug_database():
    """Test database connection"""
    print("🔍 Testing database...")
    
    try:
        from job_tracker.database import DatabaseConnection
        db = DatabaseConnection()
        
        # Test basic query
        result = db.execute_single_query("SELECT 1 as test")
        if result and result.get('test') == 1:
            print("  ✅ Database connection successful")
        else:
            print("  ❌ Database query failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def debug_auth():
    """Test authentication system"""
    print("🔍 Testing authentication...")
    
    try:
        from auth_utils import auth_manager
        
        # Test that auth manager initializes
        print(f"  - Auth manager initialized: {auth_manager is not None}")
        
        # Test database operations (without session)
        exists = auth_manager.user_repo.username_exists("nonexistent_user")
        print(f"  - Username check works: {not exists}")
        
        print("  ✅ Authentication system basic test passed")
        
    except Exception as e:
        print(f"  ❌ Authentication test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def debug_flask_app():
    """Test Flask app creation"""
    print("🔍 Testing Flask app creation...")
    
    try:
        from datetime import timedelta
        from flask import Flask
        from flask_cors import CORS
        from flask_session import Session
        
        app = Flask(__name__)
        CORS(app)
        
        app.config["SECRET_KEY"] = "test-secret-key"
        app.config["SESSION_TYPE"] = "filesystem"
        app.config["SESSION_PERMANENT"] = False
        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
        
        Session(app)
        
        print("  ✅ Flask app creation successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🐛 Job Application Tracker - Debug Mode")
    print("=" * 50)
    
    # Test each component
    tests = [
        ("Imports", debug_imports),
        ("Database", debug_database), 
        ("Authentication", debug_auth),
        ("Flask App", debug_flask_app),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} Test:")
        if not test_func():
            all_passed = False
            print(f"❌ {test_name} test failed!")
        else:
            print(f"✅ {test_name} test passed!")
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The app should start normally.")
        print("💡 Try running: python3 app.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("💡 Try running: python3 migrate_db.py first")
    
    return all_passed

if __name__ == "__main__":
    main()
