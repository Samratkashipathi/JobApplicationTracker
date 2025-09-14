#!/usr/bin/env python3
"""
Job Application Tracker - Web Interface Launcher
Quick launcher for the web interface
"""

if __name__ == "__main__":
    from app import app

    print("🚀 Starting Job Application Tracker Web Interface...")
    print("📊 Dashboard: http://localhost:5050")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host="0.0.0.0", port=5000)
