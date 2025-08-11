"""
Database module for the E-commerce Price Tracker & Notifier application.
Handles all database operations including schema creation, data insertion, and queries.
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations for the price tracker application."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Get a database connection with proper configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        current_price REAL,
                        threshold_price REAL NOT NULL,
                        site_type TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        check_interval INTEGER DEFAULT 3600
                    )
                ''')
                
                # Create price_history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL,
                        price REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Create notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL,
                        old_price REAL NOT NULL,
                        new_price REAL NOT NULL,
                        threshold_price REAL NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        email_sent BOOLEAN DEFAULT 0,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_url ON products(url)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_product ON notifications(product_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_product(self, product_name: str, url: str, threshold_price: float, 
                   site_type: str, check_interval: int = None) -> int:
        """Add a new product to track."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (product_name, url, threshold_price, site_type, check_interval)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product_name, url, threshold_price, site_type, 
                     check_interval or Config.DEFAULT_CHECK_INTERVAL))
                
                product_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added product: {product_name} with ID: {product_id}")
                return product_id
                
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            raise
    
    def get_all_products(self, active_only: bool = True) -> List[Dict]:
        """Get all products from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM products 
                    WHERE is_active = ? 
                    ORDER BY last_checked ASC
                ''' if active_only else 'SELECT * FROM products ORDER BY last_checked ASC'
                
                cursor.execute(query, (1,) if active_only else ())
                products = [dict(row) for row in cursor.fetchall()]
                return products
                
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None
    
    def update_product_price(self, product_id: int, new_price: float):
        """Update the current price of a product and add to price history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Update current price and last_checked
                cursor.execute('''
                    UPDATE products 
                    SET current_price = ?, last_checked = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_price, product_id))
                
                # Add to price history
                cursor.execute('''
                    INSERT INTO price_history (product_id, price)
                    VALUES (?, ?)
                ''', (product_id, new_price))
                
                conn.commit()
                logger.info(f"Updated price for product {product_id}: {new_price}")
                
        except Exception as e:
            logger.error(f"Error updating product price: {e}")
            raise
    
    def get_price_history(self, product_id: int, days: int = 30) -> List[Dict]:
        """Get price history for a product over the specified number of days."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT price, timestamp 
                    FROM price_history 
                    WHERE product_id = ? 
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp ASC
                '''.format(days), (product_id,))
                
                history = [dict(row) for row in cursor.fetchall()]
                return history
                
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []
    
    def add_notification(self, product_id: int, old_price: float, 
                        new_price: float, threshold_price: float) -> int:
        """Add a new price drop notification."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO notifications 
                    (product_id, old_price, new_price, threshold_price)
                    VALUES (?, ?, ?, ?)
                ''', (product_id, old_price, new_price, threshold_price))
                
                notification_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added notification for product {product_id}")
                return notification_id
                
        except Exception as e:
            logger.error(f"Error adding notification: {e}")
            raise
    
    def mark_notification_sent(self, notification_id: int):
        """Mark a notification as sent."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE notifications 
                    SET email_sent = 1 
                    WHERE id = ?
                ''', (notification_id,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error marking notification as sent: {e}")
            raise
    
    def get_pending_notifications(self) -> List[Dict]:
        """Get all notifications that haven't been sent yet."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT n.*, p.product_name, p.url 
                    FROM notifications n
                    JOIN products p ON n.product_id = p.id
                    WHERE n.email_sent = 0
                    ORDER BY n.sent_at ASC
                ''')
                
                notifications = [dict(row) for row in cursor.fetchall()]
                return notifications
                
        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []
    
    def deactivate_product(self, product_id: int):
        """Deactivate a product (stop tracking)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE products 
                    SET is_active = 0 
                    WHERE id = ?
                ''', (product_id,))
                conn.commit()
                logger.info(f"Deactivated product {product_id}")
                
        except Exception as e:
            logger.error(f"Error deactivating product: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """Get application statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total products
                cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
                total_products = cursor.fetchone()[0]
                
                # Products with price drops
                cursor.execute('''
                    SELECT COUNT(DISTINCT product_id) 
                    FROM notifications 
                    WHERE email_sent = 1
                ''')
                products_with_drops = cursor.fetchone()[0]
                
                # Total notifications sent
                cursor.execute('SELECT COUNT(*) FROM notifications WHERE email_sent = 1')
                total_notifications = cursor.fetchone()[0]
                
                # Average price drop percentage
                cursor.execute('''
                    SELECT AVG(((old_price - new_price) / old_price) * 100)
                    FROM notifications 
                    WHERE email_sent = 1
                ''')
                avg_drop_percent = cursor.fetchone()[0] or 0
                
                return {
                    'total_products': total_products,
                    'products_with_drops': products_with_drops,
                    'total_notifications': total_notifications,
                    'avg_drop_percent': round(avg_drop_percent, 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
