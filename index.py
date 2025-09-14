# DEPRECATED: This file is kept for backward compatibility
# Please use main.py instead for the new modular structure

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main
    print("⚠️  NOTICE: index.py is deprecated. Please use 'python main.py' instead.")
    print("   The application will continue with the new modular structure.\n")
    main()
except ImportError as e:
    print(f"Error importing new modular structure: {e}")
    print("Please ensure all files are properly installed.")
    sys.exit(1)