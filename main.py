#!/usr/bin/env python3
"""
Job Application Tracker - Main Entry Point
A modular command-line tool to track job applications across different job hunting seasons.
"""

import sys
import os

# Add the current directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_tracker.ui import JobTrackerCLI


def main():
    """Main application entry point"""
    try:
        cli = JobTrackerCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
