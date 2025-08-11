#!/usr/bin/env python3
"""
Setup script for the E-commerce Price Tracker & Notifier application.
Helps users install dependencies and configure the application.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🛒 E-commerce Price Tracker & Notifier Setup       ║
║                                                              ║
║  This script will help you set up the price tracker         ║
║  application on your system.                                 ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_pip():
    """Check if pip is available."""
    print("📦 Checking pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available. Please install pip first.")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements
        print("   Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_playwright():
    """Install Playwright browsers."""
    print("🌐 Installing Playwright browsers...")
    
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True)
        print("✅ Playwright browsers installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    print("⚙️  Setting up configuration...")
    
    env_template = "env_example.txt"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"   {env_file} already exists, skipping...")
        return True
    
    if not os.path.exists(env_template):
        print(f"❌ Template file {env_template} not found")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print(f"✅ Created {env_file} from template")
        print("   Please edit .env file with your email settings")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_tests():
    """Run application tests."""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_app.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("""
🎉 Setup completed successfully!

📋 Next Steps:
1. Edit the .env file with your email settings:
   - SMTP_USERNAME: Your email address
   - SMTP_PASSWORD: Your email password or app password
   - EMAIL_RECIPIENT: Where to send notifications

2. For Gmail users:
   - Enable 2-factor authentication
   - Generate an App Password for "Mail"
   - Use the App Password in SMTP_PASSWORD

3. Start the application:
   - Web Dashboard: python dashboard.py
   - Command Line: python cli.py --help
   - Background Daemon: python cli.py start-daemon

4. Add your first product:
   - Via Web: Open http://localhost:5000
   - Via CLI: python cli.py add-product "URL" THRESHOLD_PRICE

📚 For more information, see README.md
    """)

def main():
    """Main setup function."""
    print_banner()
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Pip Check", check_pip),
        ("Install Dependencies", install_dependencies),
        ("Install Playwright", install_playwright),
        ("Create Config", create_env_file),
        ("Run Tests", run_tests),
    ]
    
    print("🚀 Starting setup process...\n")
    
    for step_name, step_func in steps:
        print(f"📋 {step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the issue and run setup again.")
            return False
        print()
    
    show_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
