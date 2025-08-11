"""
Main price tracker module for the E-commerce Price Tracker & Notifier application.
Orchestrates scraping, database operations, and notifications.
"""
import logging
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import DatabaseManager
from scraper import ScrapingManager
from notifier import NotificationManager
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PriceTracker:
    """Main price tracker application that orchestrates all operations."""
    
    def __init__(self):
        """Initialize the price tracker with all components."""
        self.db = DatabaseManager()
        self.scraper = ScrapingManager()
        self.notifier = NotificationManager()
        self.is_running = False
        
        logger.info("Price Tracker initialized successfully")
    
    def add_product(self, url: str, threshold_price: float, 
                   product_name: str = None, check_interval: int = None) -> Dict:
        """Add a new product to track."""
        try:
            logger.info(f"Adding product: {url} with threshold: {threshold_price}")
            
            # First, scrape the product to get current information
            scraped_data = self.scraper.scrape_with_retry(url)
            
            if not scraped_data:
                return {
                    'success': False,
                    'error': 'Could not scrape product information from URL'
                }
            
            # Use scraped product name if not provided
            if not product_name:
                product_name = scraped_data['product_name']
            
            # Add to database
            product_id = self.db.add_product(
                product_name=product_name,
                url=url,
                threshold_price=threshold_price,
                site_type=scraped_data['site_type'],
                check_interval=check_interval
            )
            
            # Update with current price
            self.db.update_product_price(product_id, scraped_data['price'])
            
            logger.info(f"Successfully added product: {product_name} (ID: {product_id})")
            
            return {
                'success': True,
                'product_id': product_id,
                'product_name': product_name,
                'current_price': scraped_data['price'],
                'threshold_price': threshold_price
            }
            
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_product_price(self, product_id: int) -> Dict:
        """Check the current price of a specific product."""
        try:
            # Get product information
            product = self.db.get_product_by_id(product_id)
            if not product:
                return {
                    'success': False,
                    'error': f'Product with ID {product_id} not found'
                }
            
            logger.info(f"Checking price for product: {product['product_name']}")
            
            # Scrape current price
            scraped_data = self.scraper.scrape_with_retry(product['url'])
            
            if not scraped_data:
                return {
                    'success': False,
                    'error': 'Could not scrape current price'
                }
            
            old_price = product['current_price']
            new_price = scraped_data['price']
            
            # Update database with new price
            self.db.update_product_price(product_id, new_price)
            
            # Check if price dropped below threshold
            price_dropped = False
            notification_created = False
            
            if new_price <= product['threshold_price'] and old_price and new_price < old_price:
                price_dropped = True
                
                # Create notification
                notification_id = self.db.add_notification(
                    product_id=product_id,
                    old_price=old_price,
                    new_price=new_price,
                    threshold_price=product['threshold_price']
                )
                notification_created = True
                
                logger.info(f"Price drop detected for {product['product_name']}: {old_price} → {new_price}")
            
            return {
                'success': True,
                'product_name': product['product_name'],
                'old_price': old_price,
                'new_price': new_price,
                'threshold_price': product['threshold_price'],
                'price_dropped': price_dropped,
                'notification_created': notification_created
            }
            
        except Exception as e:
            logger.error(f"Error checking product price: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_all_products(self) -> Dict:
        """Check prices for all active products."""
        try:
            products = self.db.get_all_products(active_only=True)
            
            if not products:
                logger.info("No active products to check")
                return {
                    'success': True,
                    'products_checked': 0,
                    'price_drops': 0,
                    'errors': []
                }
            
            logger.info(f"Checking prices for {len(products)} products")
            
            results = {
                'success': True,
                'products_checked': 0,
                'price_drops': 0,
                'errors': []
            }
            
            for product in products:
                try:
                    check_result = self.check_product_price(product['id'])
                    
                    if check_result['success']:
                        results['products_checked'] += 1
                        if check_result.get('price_dropped'):
                            results['price_drops'] += 1
                    else:
                        results['errors'].append(f"Product {product['product_name']}: {check_result['error']}")
                        
                except Exception as e:
                    logger.error(f"Error checking product {product['product_name']}: {e}")
                    results['errors'].append(f"Product {product['product_name']}: {str(e)}")
                
                # Small delay between requests to be respectful
                time.sleep(2)
            
            logger.info(f"Price check completed: {results['products_checked']} checked, {results['price_drops']} drops")
            return results
            
        except Exception as e:
            logger.error(f"Error checking all products: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_notifications(self) -> Dict:
        """Process all pending notifications and send emails."""
        try:
            pending_notifications = self.db.get_pending_notifications()
            
            if not pending_notifications:
                logger.info("No pending notifications to process")
                return {
                    'success': True,
                    'notifications_processed': 0,
                    'emails_sent': 0
                }
            
            logger.info(f"Processing {len(pending_notifications)} pending notifications")
            
            # Process notifications
            notification_results = self.notifier.process_notifications(pending_notifications)
            
            # Mark notifications as sent
            for notification in pending_notifications:
                self.db.mark_notification_sent(notification['id'])
            
            logger.info(f"Notification processing completed: {notification_results}")
            
            return {
                'success': True,
                'notifications_processed': len(pending_notifications),
                'emails_sent': notification_results['individual_emails_sent'] + notification_results['summary_emails_sent'],
                'failed_emails': notification_results['failed_emails']
            }
            
        except Exception as e:
            logger.error(f"Error processing notifications: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_price_check_cycle(self):
        """Run a complete price check cycle."""
        try:
            logger.info("Starting price check cycle")
            
            # Check all product prices
            check_results = self.check_all_products()
            
            if not check_results['success']:
                logger.error(f"Price check failed: {check_results['error']}")
                return
            
            # Process notifications
            notification_results = self.process_notifications()
            
            if not notification_results['success']:
                logger.error(f"Notification processing failed: {notification_results['error']}")
                return
            
            logger.info(f"Price check cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in price check cycle: {e}")
    
    def start_scheduler(self):
        """Start the scheduled price checking."""
        try:
            logger.info("Starting price tracker scheduler")
            
            # Schedule price checks every hour
            schedule.every().hour.do(self.run_price_check_cycle)
            
            # Also run once immediately
            self.run_price_check_cycle()
            
            self.is_running = True
            
            logger.info("Scheduler started successfully")
            
            # Keep the scheduler running
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduled price checking."""
        logger.info("Stopping price tracker scheduler")
        self.is_running = False
        schedule.clear()
        self.scraper.cleanup()
    
    def get_statistics(self) -> Dict:
        """Get application statistics."""
        try:
            db_stats = self.db.get_statistics()
            
            # Get recent activity
            recent_products = self.db.get_all_products(active_only=True)
            recent_notifications = self.db.get_pending_notifications()
            
            return {
                'database_stats': db_stats,
                'active_products': len(recent_products),
                'pending_notifications': len(recent_notifications),
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}
    
    def test_scraping(self, url: str) -> Dict:
        """Test scraping capabilities for a URL."""
        try:
            return self.scraper.scraper.test_scraping(url)
        except Exception as e:
            logger.error(f"Error testing scraping: {e}")
            return {'error': str(e)}
    
    def test_email_configuration(self) -> Dict:
        """Test email configuration."""
        try:
            return self.notifier.test_configuration()
        except Exception as e:
            logger.error(f"Error testing email configuration: {e}")
            return {'error': str(e)}
    
    def export_price_history(self, product_id: int, format: str = 'csv') -> Dict:
        """Export price history for a product."""
        try:
            history = self.db.get_price_history(product_id, days=30)
            
            if format.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['Date', 'Price'])
                
                for entry in history:
                    writer.writerow([entry['timestamp'], entry['price']])
                
                return {
                    'success': True,
                    'format': 'csv',
                    'data': output.getvalue(),
                    'filename': f'price_history_{product_id}.csv'
                }
            
            return {
                'success': True,
                'format': 'json',
                'data': history
            }
            
        except Exception as e:
            logger.error(f"Error exporting price history: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Main function to run the price tracker."""
    tracker = PriceTracker()
    
    try:
        print("🚀 Starting E-commerce Price Tracker & Notifier")
        print("Press Ctrl+C to stop")
        
        tracker.start_scheduler()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping Price Tracker...")
        tracker.stop_scheduler()
        print("✅ Price Tracker stopped successfully")

if __name__ == "__main__":
    main()
