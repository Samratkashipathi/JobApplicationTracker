# Job Application Tracker

A beautiful web application and command-line tool to track job applications across different job hunting seasons using SQLite database.

## Features

### 🌟 Beautiful Web Interface

- **Modern Dashboard**: Clean, responsive design with real-time statistics
- **Interactive Charts**: Visual representation of application status and timeline
- **Easy Job Management**: Add, edit, and update job applications with intuitive forms
- **Advanced Search & Filtering**: Find jobs by company, role, status, or source
- **Season Management**: Create, switch between, and manage different job hunting periods
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

### 💻 Command Line Interface

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

#### 🌟 Web Interface (Recommended)

```bash
# Start the web server
python app.py
# or
python web.py

# Open your browser to: http://localhost:5000
```

#### 💻 Command Line Interface

```bash
# CLI version
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
- Flask (for web interface)
- Flask-CORS (for web interface)

## Database

Data is stored locally in `job_tracker.db` SQLite file. Back up this file to preserve your job search history.

## License

MIT License

---

**Happy job hunting! 🚀**
