#!/usr/bin/env python3
"""
Main entry point for the Price Tracker & Notifier application.
Provides easy access to all major functionalities.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("""
🛒 Price Tracker & Notifier

Usage:
  python main.py dashboard     # Start web dashboard
  python main.py cli           # Start command-line interface
  python main.py setup         # Run setup script
  python main.py test          # Run tests

Examples:
  python main.py dashboard
  python main.py cli add-product "https://amazon.com/product" 1000
        """)
        return

    command = sys.argv[1].lower()
    
    if command == 'dashboard':
        from web.dashboard_simple import main as dashboard_main
        dashboard_main()
    elif command == 'cli':
        from utils.cli import main as cli_main
        cli_main()
    elif command == 'setup':
        from setup import main as setup_main
        setup_main()
    elif command == 'test':
        from utils.test_app import main as test_main
        test_main()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python main.py' to see available commands")

if __name__ == "__main__":
    main()
