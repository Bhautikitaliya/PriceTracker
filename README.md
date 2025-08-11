# 🛒 E-commerce Price Tracker & Notifier

A comprehensive, production-ready Python application that monitors product prices from Amazon and Flipkart, tracks price history, and sends email notifications when prices drop below your threshold.

## ✨ Features

### 🔍 Web Scraping
- **Multi-site Support**: Amazon (including Amazon India - amzn.in), Amazon.com, and Flipkart
- **Dual Scraping Methods**: BeautifulSoup for static content, Playwright for JavaScript-heavy pages
- **Intelligent Fallback**: Automatically switches between scraping methods
- **Robust Error Handling**: Retry logic and comprehensive exception handling

### 📊 Database & Price History
- **SQLite Database**: Lightweight, no external database required
- **Comprehensive Schema**: Products, price history, and notifications tracking
- **Historical Data**: Track price changes over time with timestamps
- **Performance Optimized**: Indexed queries for fast data retrieval

### 📧 Email Notifications
- **SMTP Integration**: Support for Gmail, Outlook, and other email providers
- **Beautiful HTML Emails**: Professional-looking price drop alerts
- **Batch Processing**: Summary emails for multiple price drops
- **Configurable**: Easy email settings management

### 📈 Dashboard & Analytics
- **Web Dashboard**: Modern HTML interface with Bootstrap
- **Real-time Statistics**: Track active products, price drops, and notifications
- **Interactive Charts**: Plotly-powered price history visualizations
- **Export Features**: CSV export for price history data
- **Responsive Design**: Works on desktop and mobile devices

### ⚙️ Configuration & Management
- **Environment Variables**: Secure configuration management
- **Flexible Settings**: Customizable check intervals, thresholds, and email settings
- **Testing Tools**: Built-in scraping and email configuration testing
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd price-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (for dynamic content scraping)
   ```bash
   playwright install chromium
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your settings
   # At minimum, configure your email settings
   ```

### Email Configuration

For Gmail users:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use this app password in your `.env` file

Example `.env` configuration:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENT=your-email@gmail.com
```

## 📖 Usage

### Running the Application

#### Option 1: Web Dashboard (Recommended)
```bash
python dashboard.py
```
- Open your browser to `http://localhost:5000`
- Use the web interface to manage products and view statistics

#### Option 2: Command Line Tracker
```bash
python price_tracker.py
```
- Runs the price tracker in the background
- Automatically checks prices every hour
- Sends email notifications for price drops

### Adding Products

#### Via Web Dashboard
1. Open the dashboard in your browser
2. Click "Add Product" button
3. Enter the product URL (Amazon or Flipkart)
4. Set your desired threshold price
5. Click "Add Product"

#### Via Python Code
```python
from price_tracker import PriceTracker

tracker = PriceTracker()
result = tracker.add_product(
    url="https://amazon.in/product-url",
    threshold_price=999.99,
    product_name="Optional Product Name"
)
```

### Monitoring and Management

#### View Statistics
- Dashboard shows real-time statistics
- Track active products, price drops, and notifications sent
- View average price drop percentages

#### Price History Charts
- Click the chart icon next to any product
- View interactive price history over time
- Export data as CSV for further analysis

#### Testing Tools
- **Test Scraping**: Verify that the scraper can extract data from a URL
- **Test Email**: Verify your email configuration is working
- **Manual Price Check**: Check individual product prices on demand

## 🏗️ Architecture

### Core Components

1. **`config.py`** - Configuration management
2. **`database.py`** - SQLite database operations
3. **`scraper.py`** - Web scraping with BeautifulSoup and Playwright
4. **`notifier.py`** - Email notification system
5. **`price_tracker.py`** - Main application orchestrator
6. **`dashboard.py`** - Flask web dashboard

### Database Schema

```sql
-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    current_price REAL,
    threshold_price REAL NOT NULL,
    site_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_interval INTEGER DEFAULT 3600
);

-- Price history table
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    old_price REAL NOT NULL,
    new_price REAL NOT NULL,
    threshold_price REAL NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_sent BOOLEAN DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | SQLite database file path | `price_tracker.db` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | Email username | - |
| `SMTP_PASSWORD` | Email password/app password | - |
| `EMAIL_RECIPIENT` | Email recipient address | - |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` |
| `DEFAULT_CHECK_INTERVAL` | Price check interval (seconds) | `3600` |
| `PRICE_DROP_THRESHOLD_PERCENT` | Minimum price drop % for notification | `5.0` |
| `DASHBOARD_HOST` | Dashboard host address | `localhost` |
| `DASHBOARD_PORT` | Dashboard port | `5000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🛠️ Advanced Usage

### Custom Scraping Selectors

The application includes pre-configured selectors for Amazon and Flipkart. To add support for new sites:

1. Edit `config.py`
2. Add new site configuration to `SUPPORTED_SITES`
3. Define price and title selectors

### Custom Email Templates

Email templates are defined in `notifier.py`. You can customize:
- HTML email styling
- Email subject lines
- Content layout and formatting

### Scheduling Customization

Modify the scheduling in `price_tracker.py`:
```python
# Check every 30 minutes instead of hourly
schedule.every(30).minutes.do(self.run_price_check_cycle)

# Check at specific times
schedule.every().day.at("10:00").do(self.run_price_check_cycle)
schedule.every().day.at("18:00").do(self.run_price_check_cycle)
```

## 🐛 Troubleshooting

### Common Issues

1. **Scraping fails**
   - Check if the website structure has changed
   - Try the "Test Scraping" feature in the dashboard
   - Verify the URL is accessible

2. **Email not sending**
   - Verify SMTP credentials in `.env`
   - Check if 2FA is enabled (for Gmail)
   - Use App Password instead of regular password
   - Test email configuration in dashboard

3. **Playwright issues**
   - Run `playwright install chromium`
   - Ensure you have sufficient disk space
   - Check system requirements for Playwright

4. **Database errors**
   - Check file permissions for database directory
   - Ensure sufficient disk space
   - Verify SQLite is working properly

### Logs

Check the log file (`price_tracker.log` by default) for detailed error information:
```bash
tail -f price_tracker.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **BeautifulSoup** for HTML parsing
- **Playwright** for dynamic content scraping
- **Flask** for the web dashboard
- **Plotly** for interactive charts
- **Bootstrap** for responsive UI design

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on the repository
4. Check the documentation for configuration options

---

**Happy Price Tracking! 🎉**
