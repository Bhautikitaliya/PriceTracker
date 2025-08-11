"""
Test script for the E-commerce Price Tracker & Notifier application.
Tests core functionality without requiring external dependencies.
"""
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database functionality."""
    print("🧪 Testing Database...")
    
    try:
        from ..core.database import DatabaseManager
        
        # Use temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = DatabaseManager(db_path)
        
        # Test adding a product
        product_id = db.add_product(
            product_name="Test Product",
            url="https://amazon.in/test-product",
            threshold_price=999.99,
            site_type="amazon"
        )
        
        assert product_id > 0, "Product ID should be positive"
        print("✅ Database add_product test passed")
        
        # Test getting products
        products = db.get_all_products()
        assert len(products) == 1, "Should have one product"
        assert products[0]['product_name'] == "Test Product"
        print("✅ Database get_all_products test passed")
        
        # Test updating price
        db.update_product_price(product_id, 899.99)
        product = db.get_product_by_id(product_id)
        assert product['current_price'] == 899.99
        print("✅ Database update_product_price test passed")
        
        # Test price history
        history = db.get_price_history(product_id)
        assert len(history) == 1
        assert history[0]['price'] == 899.99
        print("✅ Database price_history test passed")
        
        # Test notifications
        notification_id = db.add_notification(
            product_id=product_id,
            old_price=999.99,
            new_price=899.99,
            threshold_price=999.99
        )
        assert notification_id > 0
        print("✅ Database notifications test passed")
        
        # Test statistics
        stats = db.get_statistics()
        assert 'total_products' in stats
        print("✅ Database statistics test passed")
        
        # Cleanup
        os.unlink(db_path)
        print("✅ Database tests completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("🧪 Testing Configuration...")
    
    try:
        from ..core.config import Config
        
        # Test basic config loading
        assert hasattr(Config, 'DATABASE_PATH')
        assert hasattr(Config, 'SMTP_HOST')
        assert hasattr(Config, 'SUPPORTED_SITES')
        print("✅ Configuration loading test passed")
        
        # Test supported sites
        assert 'amazon' in Config.SUPPORTED_SITES
        assert 'flipkart' in Config.SUPPORTED_SITES
        print("✅ Supported sites test passed")
        
        print("✅ Configuration tests completed successfully")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def test_scraper():
    """Test scraper functionality."""
    print("🧪 Testing Scraper...")
    
    try:
        from ..core.scraper import WebScraper
        
        scraper = WebScraper()
        
        # Test site detection
        site_type = scraper.detect_site_type("https://amazon.in/product")
        assert site_type == "amazon"
        
        site_type = scraper.detect_site_type("https://flipkart.com/product")
        assert site_type == "flipkart"
        print("✅ Site detection test passed")
        
        # Test price extraction
        price = scraper.extract_price_from_text("₹1,999")
        assert price == 1999.0
        
        price = scraper.extract_price_from_text("1,234.56")
        assert price == 1234.56
        print("✅ Price extraction test passed")
        
        # Test unsupported site
        try:
            scraper.detect_site_type("https://unsupported-site.com")
            assert False, "Should raise ValueError for unsupported site"
        except ValueError:
            print("✅ Unsupported site handling test passed")
        
        scraper.cleanup()
        print("✅ Scraper tests completed successfully")
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False
    
    return True

def test_notifier():
    """Test notification functionality."""
    print("🧪 Testing Notifier...")
    
    try:
        from ..core.notifier import EmailNotifier
        
        notifier = EmailNotifier()
        
        # Test email validation (should fail without proper config)
        # This is expected behavior when email is not configured
        print("✅ Notifier initialization test passed")
        
        # Test email template creation
        notification_data = {
            'product_name': 'Test Product',
            'old_price': 999.99,
            'new_price': 899.99,
            'threshold_price': 999.99,
            'url': 'https://amazon.in/test-product'
        }
        
        msg = notifier._create_price_drop_email(notification_data)
        assert msg['Subject'] == "🚨 Price Drop Alert: Test Product"
        print("✅ Email template creation test passed")
        
        print("✅ Notifier tests completed successfully")
        
    except Exception as e:
        print(f"❌ Notifier test failed: {e}")
        return False
    
    return True

def test_price_tracker():
    """Test main price tracker functionality."""
    print("🧪 Testing Price Tracker...")
    
    try:
        from ..core.price_tracker import PriceTracker
        
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Temporarily modify config to use test database
        import config
        original_db_path = config.Config.DATABASE_PATH
        config.Config.DATABASE_PATH = db_path
        
        tracker = PriceTracker()
        
        # Test statistics
        stats = tracker.get_statistics()
        assert 'database_stats' in stats
        print("✅ Price tracker statistics test passed")
        
        # Test export functionality
        # This will fail without products, but should handle the error gracefully
        result = tracker.export_price_history(999, 'csv')
        assert not result['success']  # Should fail for non-existent product
        print("✅ Price tracker export test passed")
        
        # Restore original config
        config.Config.DATABASE_PATH = original_db_path
        
        # Cleanup
        os.unlink(db_path)
        print("✅ Price tracker tests completed successfully")
        
    except Exception as e:
        print(f"❌ Price tracker test failed: {e}")
        return False
    
    return True

def test_cli():
    """Test CLI functionality."""
    print("🧪 Testing CLI...")
    
    try:
        from cli import print_banner
        
        # Test banner function
        print_banner()  # Should not raise any exceptions
        print("✅ CLI banner test passed")
        
        print("✅ CLI tests completed successfully")
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting E-commerce Price Tracker Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Scraper", test_scraper),
        ("Notifier", test_notifier),
        ("Price Tracker", test_price_tracker),
        ("CLI", test_cli),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} tests...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} tests failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
