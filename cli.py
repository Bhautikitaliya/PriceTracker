"""
Command-line interface for the E-commerce Price Tracker & Notifier application.
Provides easy-to-use commands for managing products and monitoring prices.
"""
import argparse
import sys
import logging
from datetime import datetime
from price_tracker import PriceTracker
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🛒 E-commerce Price Tracker & Notifier        ║
║                                                              ║
║  Monitor Amazon & Flipkart prices, get email notifications  ║
║  when prices drop below your threshold!                     ║
╚══════════════════════════════════════════════════════════════╝
    """)

def add_product_command(args):
    """Add a new product to track."""
    try:
        tracker = PriceTracker()
        
        print(f"Adding product: {args.url}")
        print(f"Threshold price: ₹{args.threshold}")
        
        result = tracker.add_product(
            url=args.url,
            threshold_price=args.threshold,
            product_name=args.name,
            check_interval=args.interval
        )
        
        if result['success']:
            print(f"✅ Successfully added product!")
            print(f"   Product ID: {result['product_id']}")
            print(f"   Product Name: {result['product_name']}")
            print(f"   Current Price: ₹{result['current_price']}")
            print(f"   Threshold Price: ₹{result['threshold_price']}")
        else:
            print(f"❌ Failed to add product: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def list_products_command(args):
    """List all tracked products."""
    try:
        tracker = PriceTracker()
        products = tracker.db.get_all_products(active_only=not args.all)
        
        if not products:
            print("No products found.")
            return
        
        print(f"\n📋 Tracked Products ({len(products)} total):")
        print("=" * 80)
        
        for product in products:
            status = "🟢 Active" if product['is_active'] else "🔴 Inactive"
            price = f"₹{product['current_price']:.2f}" if product['current_price'] else "N/A"
            
            print(f"ID: {product['id']}")
            print(f"Name: {product['product_name']}")
            print(f"Price: {price}")
            print(f"Threshold: ₹{product['threshold_price']:.2f}")
            print(f"Site: {product['site_type']}")
            print(f"Status: {status}")
            print(f"Last Checked: {product['last_checked']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def check_product_command(args):
    """Check price for a specific product."""
    try:
        tracker = PriceTracker()
        
        print(f"Checking price for product ID: {args.product_id}")
        
        result = tracker.check_product_price(args.product_id)
        
        if result['success']:
            print(f"✅ Price check completed!")
            print(f"   Product: {result['product_name']}")
            print(f"   Old Price: ₹{result['old_price']:.2f}" if result['old_price'] else "   Old Price: N/A")
            print(f"   New Price: ₹{result['new_price']:.2f}")
            print(f"   Threshold: ₹{result['threshold_price']:.2f}")
            
            if result.get('price_dropped'):
                print("   🎉 Price drop detected!")
            else:
                print("   📊 No price drop")
        else:
            print(f"❌ Failed to check price: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def check_all_command(args):
    """Check prices for all active products."""
    try:
        tracker = PriceTracker()
        
        print("🔄 Checking prices for all active products...")
        
        result = tracker.check_all_products()
        
        if result['success']:
            print(f"✅ Price check completed!")
            print(f"   Products checked: {result['products_checked']}")
            print(f"   Price drops found: {result['price_drops']}")
            
            if result.get('errors'):
                print(f"   Errors: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"     - {error}")
        else:
            print(f"❌ Failed to check prices: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def process_notifications_command(args):
    """Process pending notifications."""
    try:
        tracker = PriceTracker()
        
        print("📧 Processing pending notifications...")
        
        result = tracker.process_notifications()
        
        if result['success']:
            print(f"✅ Notifications processed!")
            print(f"   Notifications: {result['notifications_processed']}")
            print(f"   Emails sent: {result['emails_sent']}")
            
            if result.get('failed_emails', 0) > 0:
                print(f"   Failed emails: {result['failed_emails']}")
        else:
            print(f"❌ Failed to process notifications: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def statistics_command(args):
    """Show application statistics."""
    try:
        tracker = PriceTracker()
        
        print("📊 Application Statistics:")
        print("=" * 40)
        
        stats = tracker.get_statistics()
        
        if 'error' in stats:
            print(f"❌ Error getting statistics: {stats['error']}")
            sys.exit(1)
        
        db_stats = stats['database_stats']
        
        print(f"Active Products: {db_stats['total_products']}")
        print(f"Products with Drops: {db_stats['products_with_drops']}")
        print(f"Total Notifications: {db_stats['total_notifications']}")
        print(f"Average Drop %: {db_stats['avg_drop_percent']:.1f}%")
        print(f"Pending Notifications: {stats['pending_notifications']}")
        print(f"Last Check: {stats['last_check']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def test_scraping_command(args):
    """Test scraping for a URL."""
    try:
        tracker = PriceTracker()
        
        print(f"🧪 Testing scraping for: {args.url}")
        
        result = tracker.test_scraping(args.url)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        print("📋 Test Results:")
        print("=" * 30)
        
        # Requests method
        if result['requests_method']:
            req_data = result['requests_method']
            print(f"✅ Requests Method: Success")
            print(f"   Product: {req_data['product_name']}")
            print(f"   Price: ₹{req_data['price']}")
        else:
            print("❌ Requests Method: Failed")
        
        # Playwright method
        if result['playwright_method']:
            play_data = result['playwright_method']
            print(f"✅ Playwright Method: Success")
            print(f"   Product: {play_data['product_name']}")
            print(f"   Price: ₹{play_data['price']}")
        else:
            print("❌ Playwright Method: Failed")
        
        print(f"🎯 Recommended Method: {result['recommended_method']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def test_email_command(args):
    """Test email configuration."""
    try:
        tracker = PriceTracker()
        
        print("📧 Testing email configuration...")
        
        result = tracker.test_email_configuration()
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        print("📋 Email Test Results:")
        print("=" * 25)
        
        print(f"Configuration: {'✅ Valid' if result['config_valid'] else '❌ Invalid'}")
        print(f"SMTP Connection: {'✅ Success' if result['smtp_connection'] else '❌ Failed'}")
        print(f"Authentication: {'✅ Success' if result['authentication'] else '❌ Failed'}")
        print(f"Test Email: {'✅ Sent' if result['test_email_sent'] else '❌ Failed'}")
        
        if result['test_email_sent']:
            print("\n✅ Email configuration is working correctly!")
        else:
            print("\n❌ Email configuration needs attention.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def export_history_command(args):
    """Export price history for a product."""
    try:
        tracker = PriceTracker()
        
        print(f"📊 Exporting price history for product ID: {args.product_id}")
        
        result = tracker.export_price_history(args.product_id, format=args.format)
        
        if result['success']:
            if args.format == 'csv':
                filename = result['filename']
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result['data'])
                print(f"✅ Price history exported to: {filename}")
            else:
                print("📋 Price History Data:")
                print("=" * 30)
                for entry in result['data']:
                    print(f"{entry['timestamp']}: ₹{entry['price']:.2f}")
        else:
            print(f"❌ Failed to export history: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def delete_product_command(args):
    """Delete/deactivate a product."""
    try:
        tracker = PriceTracker()
        
        print(f"🗑️  Deactivating product ID: {args.product_id}")
        
        # Get product info first
        product = tracker.db.get_product_by_id(args.product_id)
        if not product:
            print(f"❌ Product with ID {args.product_id} not found")
            sys.exit(1)
        
        print(f"Product: {product['product_name']}")
        
        if not args.force:
            confirm = input("Are you sure you want to deactivate this product? (y/N): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return
        
        tracker.db.deactivate_product(args.product_id)
        print(f"✅ Product '{product['product_name']}' deactivated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def start_daemon_command(args):
    """Start the price tracker daemon."""
    try:
        tracker = PriceTracker()
        
        print("🚀 Starting Price Tracker Daemon...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        tracker.start_scheduler()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping Price Tracker...")
        tracker.stop_scheduler()
        print("✅ Price Tracker stopped successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="E-commerce Price Tracker & Notifier CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add-product "https://amazon.in/product" 999.99
  %(prog)s list-products
  %(prog)s check-all
  %(prog)s start-daemon
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add product command
    add_parser = subparsers.add_parser('add-product', help='Add a new product to track')
    add_parser.add_argument('url', help='Product URL (Amazon or Flipkart)')
    add_parser.add_argument('threshold', type=float, help='Threshold price')
    add_parser.add_argument('--name', help='Product name (optional)')
    add_parser.add_argument('--interval', type=int, help='Check interval in seconds (optional)')
    add_parser.set_defaults(func=add_product_command)
    
    # List products command
    list_parser = subparsers.add_parser('list-products', help='List all tracked products')
    list_parser.add_argument('--all', action='store_true', help='Show inactive products too')
    list_parser.set_defaults(func=list_products_command)
    
    # Check product command
    check_parser = subparsers.add_parser('check-product', help='Check price for a specific product')
    check_parser.add_argument('product_id', type=int, help='Product ID')
    check_parser.set_defaults(func=check_product_command)
    
    # Check all command
    check_all_parser = subparsers.add_parser('check-all', help='Check prices for all active products')
    check_all_parser.set_defaults(func=check_all_command)
    
    # Process notifications command
    notify_parser = subparsers.add_parser('process-notifications', help='Process pending notifications')
    notify_parser.set_defaults(func=process_notifications_command)
    
    # Statistics command
    stats_parser = subparsers.add_parser('statistics', help='Show application statistics')
    stats_parser.set_defaults(func=statistics_command)
    
    # Test scraping command
    test_scrape_parser = subparsers.add_parser('test-scraping', help='Test scraping for a URL')
    test_scrape_parser.add_argument('url', help='URL to test')
    test_scrape_parser.set_defaults(func=test_scraping_command)
    
    # Test email command
    test_email_parser = subparsers.add_parser('test-email', help='Test email configuration')
    test_email_parser.set_defaults(func=test_email_command)
    
    # Export history command
    export_parser = subparsers.add_parser('export-history', help='Export price history for a product')
    export_parser.add_argument('product_id', type=int, help='Product ID')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')
    export_parser.set_defaults(func=export_history_command)
    
    # Delete product command
    delete_parser = subparsers.add_parser('delete-product', help='Deactivate a product')
    delete_parser.add_argument('product_id', type=int, help='Product ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=delete_product_command)
    
    # Start daemon command
    daemon_parser = subparsers.add_parser('start-daemon', help='Start the price tracker daemon')
    daemon_parser.set_defaults(func=start_daemon_command)
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
