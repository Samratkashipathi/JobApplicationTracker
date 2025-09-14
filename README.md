# Job Application Tracker

A command-line tool to track job applications across different job hunting seasons using SQLite database.

## Features

- **Season Management**: Create and manage different job hunting periods
- **Job Tracking**: Add, update, and track job applications
- **Status Updates**: Monitor progress through interview stages
- **Search & Filter**: Find jobs by company, role, or status
- **Statistics**: View application metrics and success rates
- **Data Persistence**: SQLite database for reliable data storage

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Recommended method
python main.py

# Alternative methods
python index.py
job-tracker  # if installed via pip install -e .
```

## Usage

1. **Create a Season**: Start a new job hunting period (e.g., "Sept 2024")
2. **Add Jobs**: Record job applications with company, role, and details
3. **Update Status**: Track progress from "Applied" to "Offer" or "Rejected"
4. **View Analytics**: Monitor your job search progress and statistics

## Job Status Pipeline

Applied → Phone Screen → Technical Interview → Onsite Interview → Final Interview → Offer

Also supports: Rejected, Withdrawn, On Hold

## Project Structure

```
job_tracker/
├── models/          # Data models (Job, Season, JobStatus)
├── database/        # SQLite operations and repositories
├── services/        # Business logic and validation
├── ui/             # Command-line interface and display
└── utils/          # Helper functions and utilities
```

## Requirements

- Python 3.7+
- tabulate
- colorama

## Database

Data is stored locally in `job_tracker.db` SQLite file. Back up this file to preserve your job search history.

## License

MIT License

---

**Happy job hunting! 🚀**
