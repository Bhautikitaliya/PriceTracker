"""
Core modules for the Price Tracker application.
Contains database, scraper, notifier, and main tracker logic.
"""

from .config import Config
from .database import DatabaseManager
from .scraper import WebScraper, ScrapingManager
from .notifier import EmailNotifier, NotificationManager
from .price_tracker import PriceTracker

__all__ = [
    'Config',
    'DatabaseManager', 
    'WebScraper',
    'ScrapingManager',
    'EmailNotifier',
    'NotificationManager',
    'PriceTracker'
]
