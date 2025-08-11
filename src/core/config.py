"""
Configuration settings for the E-commerce Price Tracker & Notifier application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for the application."""
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'price_tracker.db')
    
    # Email Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
    
    # Scraping Configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Headers for web scraping
    HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Price tracking settings
    DEFAULT_CHECK_INTERVAL = int(os.getenv('DEFAULT_CHECK_INTERVAL', '3600'))  # 1 hour in seconds
    PRICE_DROP_THRESHOLD_PERCENT = float(os.getenv('PRICE_DROP_THRESHOLD_PERCENT', '5.0'))  # 5% drop
    
    # Dashboard Configuration
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', 'localhost')
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '5000'))
    DASHBOARD_DEBUG = os.getenv('DASHBOARD_DEBUG', 'False').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'price_tracker.log')
    
    # Supported E-commerce sites
    SUPPORTED_SITES = {
        'amazon': {
            'domain': 'amazon',
            'price_selectors': [
                'span.a-price-whole',
                'span.a-offscreen',
                'span.a-price span.a-offscreen',
                '.a-price .a-offscreen'
            ],
            'title_selectors': [
                'span#productTitle',
                'h1#title',
                '#productTitle'
            ]
        },
        'flipkart': {
            'domain': 'flipkart',
            'price_selectors': [
                'div._30jeq3._16Jk6d',
                'div._1_WHN1',
                'span._16Jk6d'
            ],
            'title_selectors': [
                'span.B_NuCI',
                'h1._10Ermw',
                'h1[class*="title"]'
            ]
        }
    }
