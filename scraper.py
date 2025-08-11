"""
Web scraper module for the E-commerce Price Tracker & Notifier application.
Supports Amazon and Flipkart with both BeautifulSoup and Playwright for dynamic content.
"""
import re
import logging
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for extracting product information from e-commerce sites."""
    
    def __init__(self):
        """Initialize the scraper with configuration."""
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        self.playwright = None
        self.browser = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.cleanup()
    
    def cleanup(self):
        """Clean up Playwright resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def detect_site_type(self, url: str) -> str:
        """Detect the e-commerce site type from URL."""
        domain = urlparse(url).netloc.lower()
        
        # Support various Amazon domains (amazon.com, amzn.in, amazon.in, etc.)
        if 'amazon' in domain or 'amzn' in domain:
            return 'amazon'
        elif 'flipkart' in domain:
            return 'flipkart'
        else:
            raise ValueError(f"Unsupported site: {domain}")
    
    def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text containing currency symbols and formatting."""
        if not price_text:
            return None
        
        # Remove common currency symbols and formatting
        cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
        
        # Handle different number formats
        if ',' in cleaned and '.' in cleaned:
            # Format like "1,234.56"
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Format like "1,234" or "1,234,567"
            if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) == 3:
                # Likely "1,234" format
                cleaned = cleaned.replace(',', '')
            else:
                # Likely "1,234,567" format
                cleaned = cleaned.replace(',', '')
        
        try:
            price = float(cleaned)
            return price if price > 0 else None
        except ValueError:
            logger.warning(f"Could not parse price from text: {price_text}")
            return None
    
    def scrape_with_requests(self, url: str) -> Optional[Dict]:
        """Scrape product information using requests and BeautifulSoup."""
        try:
            logger.info(f"Scraping with requests: {url}")
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            site_type = self.detect_site_type(url)
            site_config = Config.SUPPORTED_SITES[site_type]
            
            # Extract product name
            product_name = None
            for selector in site_config['title_selectors']:
                element = soup.select_one(selector)
                if element:
                    product_name = element.get_text().strip()
                    break
            
            # Extract price
            price = None
            for selector in site_config['price_selectors']:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    price = self.extract_price_from_text(price_text)
                    if price:
                        break
            
            if not product_name:
                logger.warning(f"Could not extract product name from {url}")
                return None
            
            if not price:
                logger.warning(f"Could not extract price from {url}")
                return None
            
            return {
                'product_name': product_name,
                'price': price,
                'url': url,
                'site_type': site_type
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_with_playwright(self, url: str) -> Optional[Dict]:
        """Scrape product information using Playwright for JavaScript-heavy sites."""
        try:
            logger.info(f"Scraping with Playwright: {url}")
            
            if not self.playwright:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(headless=True)
            
            page = self.browser.new_page()
            
            # Set user agent and viewport
            page.set_extra_http_headers(Config.HEADERS)
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to the page
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            page.wait_for_timeout(3000)
            
            site_type = self.detect_site_type(url)
            site_config = Config.SUPPORTED_SITES[site_type]
            
            # Extract product name
            product_name = None
            for selector in site_config['title_selectors']:
                try:
                    element = page.query_selector(selector)
                    if element:
                        product_name = element.inner_text().strip()
                        break
                except Exception:
                    continue
            
            # Extract price
            price = None
            for selector in site_config['price_selectors']:
                try:
                    element = page.query_selector(selector)
                    if element:
                        price_text = element.inner_text().strip()
                        price = self.extract_price_from_text(price_text)
                        if price:
                            break
                except Exception:
                    continue
            
            page.close()
            
            if not product_name:
                logger.warning(f"Could not extract product name from {url}")
                return None
            
            if not price:
                logger.warning(f"Could not extract price from {url}")
                return None
            
            return {
                'product_name': product_name,
                'price': price,
                'url': url,
                'site_type': site_type
            }
            
        except Exception as e:
            logger.error(f"Error scraping with Playwright {url}: {e}")
            return None
    
    def scrape_product(self, url: str, use_playwright: bool = False) -> Optional[Dict]:
        """Main method to scrape product information from a URL."""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL format")
            
            # Detect site type
            site_type = self.detect_site_type(url)
            logger.info(f"Detected site type: {site_type} for URL: {url}")
            
            # Try scraping with the specified method
            if use_playwright:
                result = self.scrape_with_playwright(url)
                if result:
                    return result
                else:
                    # Fallback to requests if Playwright fails
                    logger.info("Playwright failed, trying with requests...")
                    return self.scrape_with_requests(url)
            else:
                result = self.scrape_with_requests(url)
                if result:
                    return result
                else:
                    # Fallback to Playwright if requests fails
                    logger.info("Requests failed, trying with Playwright...")
                    return self.scrape_with_playwright(url)
                    
        except Exception as e:
            logger.error(f"Error in scrape_product for {url}: {e}")
            return None
    
    def test_scraping(self, url: str) -> Dict:
        """Test scraping capabilities for a given URL."""
        results = {
            'url': url,
            'requests_method': None,
            'playwright_method': None,
            'recommended_method': None
        }
        
        try:
            # Test with requests
            results['requests_method'] = self.scrape_with_requests(url)
            
            # Test with Playwright
            results['playwright_method'] = self.scrape_with_playwright(url)
            
            # Determine recommended method
            if results['requests_method'] and results['playwright_method']:
                results['recommended_method'] = 'requests'  # Faster
            elif results['requests_method']:
                results['recommended_method'] = 'requests'
            elif results['playwright_method']:
                results['recommended_method'] = 'playwright'
            else:
                results['recommended_method'] = 'none'
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing scraping for {url}: {e}")
            results['error'] = str(e)
            return results

class ScrapingManager:
    """Manages scraping operations with retry logic and error handling."""
    
    def __init__(self):
        """Initialize the scraping manager."""
        self.scraper = WebScraper()
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def scrape_with_retry(self, url: str, use_playwright: bool = False) -> Optional[Dict]:
        """Scrape product with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{self.max_retries} for {url}")
                
                result = self.scraper.scrape_product(url, use_playwright)
                
                if result:
                    logger.info(f"Successfully scraped {url}: {result['product_name']} - {result['price']}")
                    return result
                else:
                    logger.warning(f"Scraping attempt {attempt + 1} failed for {url}")
                    
            except Exception as e:
                logger.error(f"Error in scraping attempt {attempt + 1} for {url}: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                import time
                time.sleep(self.retry_delay)
        
        logger.error(f"All scraping attempts failed for {url}")
        return None
    
    def cleanup(self):
        """Clean up resources."""
        self.scraper.cleanup()
