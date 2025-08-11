# Price Tracker & Notifier - Project Structure

## 📁 Directory Organization

```
Price Tracker/
├── 📄 main.py                    # Main entry point
├── 📄 setup.py                   # Installation script
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env                       # Environment variables (user-specific)
├── 📄 .gitignore                 # Git ignore rules
├── 📄 README.md                  # Main documentation
├── 📄 WINDOWS_SETUP_GUIDE.md     # Windows-specific setup
├── 📄 env_example.txt            # Environment template
├── 📄 PROJECT_STRUCTURE.md       # This file
│
├── 📁 src/                       # Source code
│   ├── 📄 __init__.py           # Package initialization
│   │
│   ├── 📁 core/                 # Core application logic
│   │   ├── 📄 __init__.py       # Core package exports
│   │   ├── 📄 config.py         # Configuration management
│   │   ├── 📄 database.py       # Database operations
│   │   ├── 📄 scraper.py        # Web scraping logic
│   │   ├── 📄 notifier.py       # Email notifications
│   │   └── 📄 price_tracker.py  # Main application logic
│   │
│   ├── 📁 web/                  # Web interface
│   │   ├── 📄 __init__.py       # Web package initialization
│   │   └── 📄 dashboard_simple.py # Flask web dashboard
│   │
│   └── 📁 utils/                # Utilities and tools
│       ├── 📄 __init__.py       # Utils package initialization
│       ├── 📄 cli.py            # Command-line interface
│       └── 📄 test_app.py       # Testing utilities
│
├── 📁 templates/                 # HTML templates
│   ├── 📄 dashboard.html        # Main dashboard template
│   └── 📄 error.html            # Error page template
│
└── 📁 static/                   # Static assets
    ├── 📄 style.css             # CSS styles
    └── 📄 script.js             # JavaScript functions
```

## 🏗️ Architecture Overview

### **Core Modules (`src/core/`)**
- **`config.py`**: Centralized configuration management
- **`database.py`**: SQLite database operations and schema
- **`scraper.py`**: Web scraping with BeautifulSoup and Playwright
- **`notifier.py`**: Email notification system
- **`price_tracker.py`**: Main application orchestrator

### **Web Interface (`src/web/`)**
- **`dashboard_simple.py`**: Flask web application with REST API
- Clean separation of concerns (no embedded HTML)

### **Utilities (`src/utils/`)**
- **`cli.py`**: Command-line interface for easy interaction
- **`test_app.py`**: Testing utilities and validation

### **Frontend Assets**
- **`templates/`**: HTML templates using Jinja2
- **`static/`**: CSS and JavaScript files (externalized)

## 🚀 Usage

### **Quick Start**
```bash
# Start web dashboard
python main.py dashboard

# Use command-line interface
python main.py cli add-product "https://amazon.com/product" 1000

# Run setup
python main.py setup

# Run tests
python main.py test
```

### **Direct Module Access**
```bash
# Web dashboard
python -m src.web.dashboard_simple

# CLI interface
python -m src.utils.cli

# Core functionality
python -c "from src.core.price_tracker import PriceTracker; pt = PriceTracker()"
```

## 🔧 Key Improvements

### **1. Modular Structure**
- ✅ Separated core logic from web interface
- ✅ Clean package organization with `__init__.py` files
- ✅ Proper import paths and relative imports

### **2. Code Organization**
- ✅ Externalized CSS and JavaScript from HTML
- ✅ Removed embedded HTML from Python code
- ✅ Simplified dashboard implementation

### **3. Maintainability**
- ✅ Single entry point (`main.py`)
- ✅ Clear separation of concerns
- ✅ Easy to extend and modify

### **4. Development Experience**
- ✅ Better IDE support with proper package structure
- ✅ Easier testing and debugging
- ✅ Cleaner codebase

## 📦 Package Dependencies

### **Core Dependencies**
- `requests`, `beautifulsoup4`, `lxml` - Web scraping
- `playwright` - Dynamic content scraping
- `flask`, `flask-cors` - Web framework
- `pandas`, `plotly` - Data visualization
- `schedule` - Task scheduling
- `python-dotenv` - Environment management

### **Development Dependencies**
- `matplotlib` - Chart generation
- `selenium` - Alternative scraping method

## 🎯 Benefits of This Structure

1. **Scalability**: Easy to add new features and modules
2. **Maintainability**: Clear separation of concerns
3. **Testability**: Isolated components for better testing
4. **Deployability**: Clean structure for production deployment
5. **Collaboration**: Multiple developers can work on different modules
6. **Documentation**: Self-documenting structure

## 🔄 Migration from Old Structure

The old structure had:
- ❌ Embedded HTML in Python files
- ❌ Flat file organization
- ❌ Mixed concerns in single files
- ❌ Hard to maintain and extend

The new structure provides:
- ✅ Clean separation of frontend and backend
- ✅ Modular package organization
- ✅ Easy to understand and navigate
- ✅ Professional development standards
