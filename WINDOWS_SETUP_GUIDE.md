# Windows Setup Guide for Price Tracker & Notifier

## 🚨 Common Issues and Solutions

### 1. Python Installation Issues

**Problem**: Python not found or not in PATH
**Solution**: 
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, **CHECK** "Add Python to PATH"
3. Restart your terminal/PowerShell after installation

**Verify Installation**:
```powershell
python --version
# or
py --version
```

### 2. Metadata Generation Failed Error

**Problem**: `error: metadata-generation-failed` during pip install
**Causes**: Missing Microsoft Visual C++ Build Tools

**Solution A - Install Build Tools**:
1. Download [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install with "C++ build tools" workload
3. Restart your terminal and try installation again

**Solution B - Use Pre-compiled Wheels**:
```powershell
# Use the Windows-optimized setup
python setup_windows.py
```

**Solution C - Install Individual Packages**:
```powershell
# Install packages one by one to identify problematic ones
pip install requests
pip install beautifulsoup4
pip install lxml
pip install python-dotenv
pip install schedule
pip install pandas
pip install flask
pip install flask-cors
pip install plotly
pip install matplotlib
pip install playwright
pip install selenium
```

### 3. Playwright Installation Issues

**Problem**: Playwright browsers fail to install
**Solution**:
```powershell
# Install Playwright first
pip install playwright

# Install browsers manually
playwright install

# If that fails, try with specific browser
playwright install chromium
```

### 4. Permission Issues

**Problem**: Permission denied errors
**Solution**:
1. Run PowerShell as Administrator
2. Or use user installation:
```powershell
pip install --user package_name
```

### 5. SSL Certificate Issues

**Problem**: SSL errors during package installation
**Solution**:
```powershell
# Trust the certificate store
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org package_name
```

## 🛠️ Step-by-Step Installation

### Method 1: Automated Setup (Recommended)

```powershell
# 1. Navigate to your project directory
cd "E:\Price tracker"

# 2. Run the Windows-optimized setup
python setup_windows.py
```

### Method 2: Manual Installation

```powershell
# 1. Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# 2. Install basic packages first
pip install requests beautifulsoup4 lxml python-dotenv schedule

# 3. Install data processing packages
pip install pandas matplotlib plotly

# 4. Install web framework
pip install flask flask-cors

# 5. Install web automation (choose one)
pip install playwright
# OR
pip install selenium webdriver-manager

# 6. Install Playwright browsers
playwright install
```

### Method 3: Using Virtual Environment

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate

# 3. Install packages
pip install -r requirements_windows.txt

# 4. Install Playwright browsers
playwright install
```

## 🔧 Configuration

### 1. Email Setup (Gmail Example)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to [Google Account Settings](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer"
   - Copy the generated password

3. Edit `.env` file:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
EMAIL_RECIPIENT=your_email@gmail.com
```

### 2. Alternative Email Providers

**Outlook/Hotmail**:
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo**:
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

## 🚀 Running the Application

### 1. Start the Price Tracker
```powershell
python price_tracker.py
```

### 2. Start the Dashboard
```powershell
python dashboard.py
```
Then open: http://127.0.0.1:5000

### 3. Use Command Line Interface
```powershell
# Add a product (supports Amazon.com, Amazon India, and Flipkart)
python cli.py add-product "https://amazon.com/product-url"
python cli.py add-product "https://amzn.in/product-url"
python cli.py add-product "https://flipkart.com/product-url"

# List products
python cli.py list-products

# Check all products
python cli.py check-all
```

## 🐛 Troubleshooting

### Check Python and Package Versions
```powershell
python --version
pip list
```

### Test Individual Components
```powershell
# Test scraping
python cli.py test-scraping "https://amazon.com/product-url"

# Test email
python cli.py test-email

# Test database
python test_app.py
```

### View Logs
```powershell
# Check application logs
Get-Content price_tracker.log -Tail 50
```

### Reset Database
```powershell
# Remove database file to start fresh
Remove-Item price_tracker.db
```

## 📞 Getting Help

If you encounter issues:

1. **Check the logs**: Look at `price_tracker.log` for error messages
2. **Test components**: Use the test commands in `cli.py`
3. **Verify Python**: Ensure Python 3.8+ is installed and in PATH
4. **Check dependencies**: Run `pip list` to see installed packages
5. **Try virtual environment**: Isolate the installation in a virtual environment

## 🔄 Alternative Installation Methods

### Using Conda (if you have Anaconda/Miniconda)
```powershell
# Create conda environment
conda create -n price-tracker python=3.10

# Activate environment
conda activate price-tracker

# Install packages
conda install requests beautifulsoup4 lxml pandas matplotlib flask
pip install playwright plotly python-dotenv schedule flask-cors selenium
```

### Using Chocolatey (if you have Chocolatey package manager)
```powershell
# Install Python via Chocolatey
choco install python

# Then follow the regular installation steps
```

## ✅ Verification Checklist

After installation, verify these work:

- [ ] `python --version` shows Python 3.8+
- [ ] `pip list` shows all required packages
- [ ] `python test_app.py` runs without errors
- [ ] `python cli.py test-scraping "https://amazon.com"` works
- [ ] Dashboard starts with `python dashboard.py`
- [ ] Email configuration works (if configured)

If any step fails, refer to the troubleshooting section above.
