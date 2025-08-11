#!/usr/bin/env python3
"""
Windows-specific setup script for Price Tracker & Notifier
Handles common Windows installation issues and provides alternative solutions.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("🛒 Price Tracker & Notifier - Windows Setup")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_pip():
    """Check if pip is available."""
    print("🔍 Checking pip availability...")
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        return False

def install_build_tools():
    """Install Microsoft Visual C++ Build Tools if needed."""
    print("🔧 Installing build tools...")
    try:
        # Try to install wheel and setuptools first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "wheel", "setuptools"], 
                      check=True, capture_output=True, text=True)
        print("✅ Build tools updated")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not update build tools: {e}")
        return False

def install_dependencies_windows():
    """Install dependencies with Windows-specific handling."""
    print("📦 Installing dependencies (Windows-optimized)...")
    
    # First, install packages that don't require compilation
    basic_packages = [
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "lxml==4.9.3",
        "python-dotenv==1.0.0",
        "schedule==1.2.0",
        "pandas==2.1.4"
    ]
    
    print("📦 Installing basic packages...")
    for package in basic_packages:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {package} installed successfully")
            else:
                print(f"   ⚠️  Warning: {package} installation had issues")
                print(f"      Error: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Error installing {package}: {e}")
    
    # Install packages that might need special handling
    print("📦 Installing advanced packages...")
    
    # Try to install matplotlib with pre-compiled wheel
    try:
        print("   Installing matplotlib...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib==3.8.2"], 
                      check=True, capture_output=True, text=True)
        print("   ✅ matplotlib installed successfully")
    except subprocess.CalledProcessError:
        print("   ⚠️  matplotlib installation failed, trying alternative...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib"], 
                          check=True, capture_output=True, text=True)
            print("   ✅ matplotlib installed with latest version")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ matplotlib installation failed: {e}")
    
    # Install Flask and related packages
    flask_packages = [
        "flask==3.0.0",
        "flask-cors==4.0.0"
    ]
    
    for package in flask_packages:
        try:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True, text=True)
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error installing {package}: {e}")
    
    # Install Plotly
    try:
        print("   Installing plotly...")
        subprocess.run([sys.executable, "-m", "pip", "install", "plotly==5.17.0"], 
                      check=True, capture_output=True, text=True)
        print("   ✅ plotly installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error installing plotly: {e}")
    
    # Install Playwright (this might take a while)
    try:
        print("   Installing playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright==1.40.0"], 
                      check=True, capture_output=True, text=True)
        print("   ✅ playwright installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error installing playwright: {e}")
    
    # Install Selenium as backup
    try:
        print("   Installing selenium...")
        subprocess.run([sys.executable, "-m", "pip", "install", "selenium==4.15.2"], 
                      check=True, capture_output=True, text=True)
        print("   ✅ selenium installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error installing selenium: {e}")

def install_playwright_browsers():
    """Install Playwright browsers."""
    print("🌐 Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], 
                      check=True, capture_output=True, text=True)
        print("✅ Playwright browsers installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Playwright browsers: {e}")
        print("   You can install them manually later with: playwright install")
        return False

def create_env_file():
    """Create .env file with default configuration."""
    print("⚙️  Creating .env file...")
    
    env_content = """# Price Tracker Configuration
# Database
DATABASE_PATH=price_tracker.db

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENT=your_email@gmail.com

# Scraping Configuration
REQUEST_TIMEOUT=30
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
DEFAULT_CHECK_INTERVAL=3600
PRICE_DROP_THRESHOLD_PERCENT=10

# Dashboard Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=5000
DASHBOARD_DEBUG=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=price_tracker.log
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("   📝 Please edit .env file with your email configuration")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests...")
    
    tests = [
        ("Testing imports", "import requests, bs4, flask, pandas, plotly"),
        ("Testing database", "from database import DatabaseManager; db = DatabaseManager(); print('Database OK')"),
        ("Testing config", "from config import Config; print('Config OK')"),
    ]
    
    for test_name, test_code in tests:
        try:
            print(f"   Testing {test_name}...")
            subprocess.run([sys.executable, "-c", test_code], 
                          check=True, capture_output=True, text=True)
            print(f"   ✅ {test_name} passed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ {test_name} failed: {e}")

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print("1. 📧 Configure Email Settings:")
    print("   - Edit the .env file with your email credentials")
    print("   - For Gmail, use an App Password (not your regular password)")
    print("   - Enable 2FA and generate App Password at: https://myaccount.google.com/apppasswords")
    print()
    print("2. 🚀 Start the Application:")
    print("   - Run: python price_tracker.py")
    print("   - Or use CLI: python cli.py add-product <URL>")
    print()
    print("3. 🌐 Access Dashboard:")
    print("   - Start dashboard: python dashboard.py")
    print("   - Open browser: http://127.0.0.1:5000")
    print()
    print("4. 📚 Documentation:")
    print("   - Read README.md for detailed usage instructions")
    print("   - Check test_app.py for functionality verification")
    print()
    print("5. 🔧 Troubleshooting:")
    print("   - If you encounter issues, check the logs in price_tracker.log")
    print("   - For scraping issues, try: python cli.py test-scraping <URL>")
    print("   - For email issues, try: python cli.py test-email")
    print("=" * 60)

def main():
    """Main setup function."""
    print_banner()
    
    if not check_python_version():
        return
    
    if not check_pip():
        print("❌ pip is required for installation")
        return
    
    install_build_tools()
    install_dependencies_windows()
    install_playwright_browsers()
    create_env_file()
    run_basic_tests()
    show_next_steps()

if __name__ == "__main__":
    main()
