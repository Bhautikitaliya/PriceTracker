"""
Email notification module for the E-commerce Price Tracker & Notifier application.
Handles SMTP email sending for price drop alerts.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class EmailNotifier:
    """Handles email notifications for price drops."""
    
    def __init__(self):
        """Initialize the email notifier with SMTP configuration."""
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        self.recipient = Config.EMAIL_RECIPIENT
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate email configuration."""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email notifications will be disabled.")
            return False
        
        if not self.recipient:
            logger.warning("Email recipient not configured. Email notifications will be disabled.")
            return False
        
        logger.info("Email configuration validated successfully")
        return True
    
    def _create_price_drop_email(self, notification_data: Dict) -> MIMEMultipart:
        """Create a price drop notification email."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Price Drop Alert: {notification_data['product_name']}"
        msg['From'] = self.smtp_username
        msg['To'] = self.recipient
        
        # Calculate price drop percentage
        old_price = notification_data['old_price']
        new_price = notification_data['new_price']
        price_drop = old_price - new_price
        price_drop_percent = (price_drop / old_price) * 100
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .price-drop {{ background-color: #ff6b6b; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .product-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .price-comparison {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .old-price {{ text-decoration: line-through; color: #6c757d; }}
                .new-price {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
                .cta-button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Price Drop Alert!</h1>
                    <p>Great news! The price of a product you're tracking has dropped.</p>
                </div>
                
                <div class="price-drop">
                    <h2>Price Dropped by {price_drop_percent:.1f}%</h2>
                    <p>You saved ₹{price_drop:.2f}!</p>
                </div>
                
                <div class="product-info">
                    <h3>{notification_data['product_name']}</h3>
                    <div class="price-comparison">
                        <div>
                            <span class="old-price">Old Price: ₹{old_price:.2f}</span>
                        </div>
                        <div>
                            <span class="new-price">New Price: ₹{new_price:.2f}</span>
                        </div>
                    </div>
                    <p><strong>Threshold Price:</strong> ₹{notification_data['threshold_price']:.2f}</p>
                </div>
                
                <div style="text-align: center;">
                    <a href="{notification_data['url']}" class="cta-button">View Product</a>
                </div>
                
                <div class="footer">
                    <p>This notification was sent by your Price Tracker application.</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text content
        text_content = f"""
        Price Drop Alert!
        
        Product: {notification_data['product_name']}
        Old Price: ₹{old_price:.2f}
        New Price: ₹{new_price:.2f}
        Price Drop: ₹{price_drop:.2f} ({price_drop_percent:.1f}%)
        Threshold Price: ₹{notification_data['threshold_price']:.2f}
        
        View Product: {notification_data['url']}
        
        This notification was sent by your Price Tracker application.
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Attach both HTML and text versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        return msg
    
    def _create_summary_email(self, notifications: List[Dict]) -> MIMEMultipart:
        """Create a summary email for multiple price drops."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📊 Price Tracker Summary - {len(notifications)} Price Drops"
        msg['From'] = self.smtp_username
        msg['To'] = self.recipient
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .summary {{ background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .product-item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .price-info {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .old-price {{ text-decoration: line-through; color: #6c757d; }}
                .new-price {{ color: #28a745; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Price Tracker Summary</h1>
                    <p>You have {len(notifications)} price drop(s) to review.</p>
                </div>
                
                <div class="summary">
                    <h3>Summary</h3>
                    <p>Total Products with Price Drops: {len(notifications)}</p>
                </div>
        """
        
        # Add each product
        for notification in notifications:
            old_price = notification['old_price']
            new_price = notification['new_price']
            price_drop = old_price - new_price
            price_drop_percent = (price_drop / old_price) * 100
            
            html_content += f"""
                <div class="product-item">
                    <h4>{notification['product_name']}</h4>
                    <div class="price-info">
                        <span class="old-price">₹{old_price:.2f}</span>
                        <span>→</span>
                        <span class="new-price">₹{new_price:.2f}</span>
                        <span>({price_drop_percent:.1f}% drop)</span>
                    </div>
                    <p><a href="{notification['url']}">View Product</a></p>
                </div>
            """
        
        html_content += """
                <div class="footer">
                    <p>This summary was sent by your Price Tracker application.</p>
                    <p>Timestamp: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text content
        text_content = f"Price Tracker Summary\n\nYou have {len(notifications)} price drop(s) to review.\n\n"
        
        for notification in notifications:
            old_price = notification['old_price']
            new_price = notification['new_price']
            price_drop = old_price - new_price
            price_drop_percent = (price_drop / old_price) * 100
            
            text_content += f"""
Product: {notification['product_name']}
Old Price: ₹{old_price:.2f} → New Price: ₹{new_price:.2f} ({price_drop_percent:.1f}% drop)
View Product: {notification['url']}

"""
        
        text_content += f"\nThis summary was sent by your Price Tracker application.\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Attach both HTML and text versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        return msg
    
    def send_price_drop_notification(self, notification_data: Dict) -> bool:
        """Send a single price drop notification email."""
        try:
            if not self._validate_config():
                logger.warning("Email configuration invalid. Skipping notification.")
                return False
            
            msg = self._create_price_drop_email(notification_data)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Price drop notification sent for {notification_data['product_name']}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check your email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def send_summary_notification(self, notifications: List[Dict]) -> bool:
        """Send a summary email for multiple price drops."""
        try:
            if not self._validate_config():
                logger.warning("Email configuration invalid. Skipping summary notification.")
                return False
            
            if not notifications:
                logger.info("No notifications to send in summary.")
                return True
            
            msg = self._create_summary_email(notifications)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Summary notification sent for {len(notifications)} products")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check your email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending summary notification: {e}")
            return False
    
    def test_email_configuration(self) -> Dict:
        """Test email configuration and send a test email."""
        result = {
            'config_valid': False,
            'smtp_connection': False,
            'authentication': False,
            'test_email_sent': False,
            'error': None
        }
        
        try:
            # Check configuration
            if not self._validate_config():
                result['error'] = "Invalid email configuration"
                return result
            
            result['config_valid'] = True
            
            # Test SMTP connection
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                result['smtp_connection'] = True
                
                # Test authentication
                server.login(self.smtp_username, self.smtp_password)
                result['authentication'] = True
                
                # Send test email
                test_msg = MIMEMultipart('alternative')
                test_msg['Subject'] = "🧪 Price Tracker - Test Email"
                test_msg['From'] = self.smtp_username
                test_msg['To'] = self.recipient
                
                test_content = """
                This is a test email from your Price Tracker application.
                
                If you received this email, your email configuration is working correctly!
                
                Timestamp: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                test_msg.attach(MIMEText(test_content, 'plain'))
                server.send_message(test_msg)
                result['test_email_sent'] = True
                
                logger.info("Email configuration test successful")
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Email configuration test failed: {e}")
        
        return result

class NotificationManager:
    """Manages notification operations and batch processing."""
    
    def __init__(self):
        """Initialize the notification manager."""
        self.notifier = EmailNotifier()
        self.batch_size = 5  # Send summary emails for batches larger than this
    
    def process_notifications(self, notifications: List[Dict]) -> Dict:
        """Process a list of notifications and send appropriate emails."""
        results = {
            'total_notifications': len(notifications),
            'individual_emails_sent': 0,
            'summary_emails_sent': 0,
            'failed_emails': 0,
            'errors': []
        }
        
        try:
            if not notifications:
                logger.info("No notifications to process")
                return results
            
            # If we have many notifications, send a summary email
            if len(notifications) > self.batch_size:
                logger.info(f"Sending summary email for {len(notifications)} notifications")
                if self.notifier.send_summary_notification(notifications):
                    results['summary_emails_sent'] = 1
                else:
                    results['failed_emails'] += 1
                    results['errors'].append("Failed to send summary email")
            else:
                # Send individual emails
                for notification in notifications:
                    if self.notifier.send_price_drop_notification(notification):
                        results['individual_emails_sent'] += 1
                    else:
                        results['failed_emails'] += 1
                        results['errors'].append(f"Failed to send email for {notification.get('product_name', 'Unknown')}")
            
            logger.info(f"Notification processing completed: {results}")
            
        except Exception as e:
            logger.error(f"Error processing notifications: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def test_configuration(self) -> Dict:
        """Test the email configuration."""
        return self.notifier.test_email_configuration()
