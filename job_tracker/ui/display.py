"""
Display utilities for Job Tracker UI
"""

import os
from typing import List, Dict, Optional
from tabulate import tabulate
from colorama import Fore, Back, Style, init
from ..models import Job, Season
from ..utils.date_utils import format_date, format_datetime
from ..utils.validation import truncate_text

# Initialize colorama for cross-platform colored output
init()


class DisplayManager:
    """Manages display formatting and output"""
    
    def __init__(self):
        self.table_format = "grid"
        self.max_display_length = 30
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def print_success(self, message: str):
        """Print success message in green"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    def print_error(self, message: str):
        """Print error message in red"""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    def print_warning(self, message: str):
        """Print warning message in yellow"""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    def print_info(self, message: str):
        """Print info message in blue"""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
    
    def print_menu_header(self):
        """Print the main application header"""
        print(f"{Fore.GREEN}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                  JOB APPLICATION TRACKER                  ║")
        print("║              Track Your Career Journey                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
    
    def print_main_menu(self):
        """Print the main menu"""
        print(f"\n{Fore.CYAN}╔════════════════ MAIN MENU ═══════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║  Season Management:                          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    1. Create New Season                      ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    2. End Current Season                     ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    3. View All Seasons                       ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║  Job Management:                             ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    4. Add New Job Application                ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    5. Update Job Status                      ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    6. View All Jobs                          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    7. View Job Details                       ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║  Reports & Analytics:                        ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    8. View Statistics                        ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    9. Search Jobs                            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   10. Filter by Status                       ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   11. Clear Screen                           ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║    0. Exit                                   ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    def display_season_info(self, season: Season, stats: Dict = None):
        """Display current season information"""
        print(f"\n{Fore.BLUE}Current Season: {season.name}{Style.RESET_ALL}")
        if stats and stats.get("total_jobs", 0) > 0:
            print(f"{Fore.BLUE}Total Applications: {stats['total_jobs']}{Style.RESET_ALL}")
    
    def display_no_season_warning(self):
        """Display warning when no active season exists"""
        print(f"\n{Fore.YELLOW}No active season - Create one to start tracking jobs{Style.RESET_ALL}")
    
    def display_jobs_table(self, jobs: List[Job], title: str = None):
        """Display jobs in a formatted table"""
        if title:
            self.print_header(title)
        
        if not jobs:
            self.print_warning("No jobs to display")
            return
        
        headers = ["ID", "Role", "Company Name", "Source", "Status", "Applied Date"]
        table_data = []
        
        for job in jobs:
            table_data.append([
                job.id,
                truncate_text(job.role, self.max_display_length),
                truncate_text(job.company_name, self.max_display_length),
                truncate_text(job.source or "N/A", 15),
                job.current_status.value,
                format_date(job.applied_date)
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt=self.table_format))
        print(f"\n{Fore.BLUE}Total records: {len(jobs)}{Style.RESET_ALL}")
    
    def display_seasons_table(self, seasons: List[Season], title: str = "All Seasons"):
        """Display seasons in a formatted table"""
        self.print_header(title)
        
        if not seasons:
            self.print_warning("No seasons found")
            return
        
        headers = ["ID", "Name", "Start Date", "End Date", "Status"]
        table_data = []
        
        for season in seasons:
            status = "Active" if season.is_active else "Ended"
            end_date = format_date(season.end_date) if season.end_date else "N/A"
            
            table_data.append([
                season.id,
                truncate_text(season.name, 25),
                format_date(season.start_date),
                end_date,
                status
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt=self.table_format))
    
    def display_job_details(self, job: Job):
        """Display detailed information for a specific job"""
        self.print_header("Job Details")
        
        print(f"{Fore.CYAN}Job Information:{Style.RESET_ALL}")
        print(f"ID: {job.id}")
        print(f"Role: {job.role}")
        print(f"Company: {job.company_name}")
        print(f"Website: {job.company_website or 'N/A'}")
        print(f"Source: {job.source or 'N/A'}")
        print(f"Status: {job.current_status.value}")
        print(f"Season: {job.season_name or 'N/A'}")
        print(f"Applied Date: {format_datetime(job.applied_date)}")
        print(f"Last Updated: {format_datetime(job.last_updated)}")
        print(f"Days Since Applied: {job.days_since_applied}")
        print(f"Resume Sent: {job.resume_sent or 'N/A'}")
        print(f"\nJob Description:")
        print(f"{job.job_description or 'N/A'}")
    
    def display_statistics(self, season: Season, stats: Dict):
        """Display job application statistics"""
        self.print_header("Job Application Statistics")
        
        self.print_info(f"Season: {season.name}")
        
        if not stats or stats.get("total_jobs", 0) == 0:
            self.print_warning("No statistics available")
            return
        
        print(f"\n{Fore.CYAN}Overall Statistics:{Style.RESET_ALL}")
        print(f"Total Applications: {stats['total_jobs']}")
        
        if stats.get("status_breakdown"):
            print(f"\n{Fore.CYAN}Status Breakdown:{Style.RESET_ALL}")
            for status, count in stats["status_breakdown"].items():
                percentage = (count / stats["total_jobs"]) * 100 if stats["total_jobs"] > 0 else 0
                print(f"{status}: {count} ({percentage:.1f}%)")
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation"""
        while True:
            value = input(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}").strip()
            if value or not required:
                return value
            self.print_error("This field is required. Please enter a value.")
    
    def get_date_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """Get date input from user with format validation"""
        from ..utils.date_utils import parse_date
        
        full_prompt = f"{prompt} (YYYY-MM-DD, MM/DD/YYYY, or leave empty for today): "
        
        while True:
            date_str = input(f"{Fore.YELLOW}{full_prompt}{Style.RESET_ALL}").strip()
            
            # If empty and not required, return None
            if not date_str:
                if not required:
                    return None
                else:
                    return None  # Will use current date as default
            
            # Try to parse the date
            try:
                parsed_date = parse_date(date_str)
                if parsed_date:
                    return date_str
                else:
                    self.print_error("Unable to parse date. Please use format: YYYY-MM-DD or MM/DD/YYYY")
            except ValueError as e:
                self.print_error(f"Invalid date format: {str(e)}")
                self.print_info("Please use format: YYYY-MM-DD (e.g., 2024-09-15) or MM/DD/YYYY (e.g., 09/15/2024)")
    
    def get_choice(self, prompt: str, choices: List[str], allow_empty: bool = False) -> Optional[str]:
        """Get user choice from a list of options"""
        print(f"\n{Fore.CYAN}Available options:{Style.RESET_ALL}")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        if allow_empty:
            print("0. Skip/Leave empty")
        
        while True:
            try:
                choice_input = input(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}").strip()
                if not choice_input and allow_empty:
                    return None
                
                choice_num = int(choice_input)
                if allow_empty and choice_num == 0:
                    return None
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    self.print_error(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                self.print_error("Please enter a valid number")
    
    def confirm_action(self, message: str) -> bool:
        """Get confirmation from user"""
        while True:
            response = input(f"{Fore.YELLOW}{message} (y/n): {Style.RESET_ALL}").lower().strip()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                self.print_error("Please enter 'y' for yes or 'n' for no")
    
    def pause(self):
        """Pause and wait for user input"""
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
