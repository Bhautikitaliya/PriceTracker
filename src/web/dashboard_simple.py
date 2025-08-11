"""
Simplified web dashboard for the E-commerce Price Tracker & Notifier application.
Uses external HTML templates instead of embedding them in Python code.
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import plotly.graph_objs as go
import plotly.utils
import pandas as pd
import os

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.price_tracker import PriceTracker
from core.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='../../templates',  # Point to templates directory
           static_folder='../../static')       # Point to static directory
CORS(app)

# Initialize price tracker
tracker = PriceTracker()

@app.route('/')
def index():
    """Main dashboard page."""
    try:
        # Get statistics
        stats = tracker.get_statistics()
        
        # Get all products
        products = tracker.db.get_all_products(active_only=False)
        
        return render_template('dashboard.html', stats=stats, products=products)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/products', methods=['GET'])
def get_products():
    """API endpoint to get all products."""
    try:
        products = tracker.db.get_all_products(active_only=False)
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products', methods=['POST'])
def add_product():
    """API endpoint to add a new product."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data or 'threshold_price' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        result = tracker.add_product(
            url=data['url'],
            threshold_price=float(data['threshold_price']),
            product_name=data.get('product_name'),
            check_interval=data.get('check_interval')
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """API endpoint to deactivate a product."""
    try:
        tracker.db.deactivate_product(product_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/<int:product_id>/check', methods=['POST'])
def check_product(product_id):
    """API endpoint to manually check a product's price."""
    try:
        result = tracker.check_product_price(product_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error checking product: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/<int:product_id>/history')
def get_price_history(product_id):
    """API endpoint to get price history for a product."""
    try:
        days = request.args.get('days', 30, type=int)
        history = tracker.db.get_price_history(product_id, days=days)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/<int:product_id>/chart')
def get_price_chart(product_id):
    """API endpoint to get price history chart data."""
    try:
        days = request.args.get('days', 30, type=int)
        history = tracker.db.get_price_history(product_id, days=days)
        
        if not history:
            return jsonify({'success': False, 'error': 'No price history available'})
        
        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create Plotly chart
        trace = go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines+markers',
            name='Price',
            line=dict(color='#007bff', width=2),
            marker=dict(size=6)
        )
        
        layout = go.Layout(
            title='Price History',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Price (₹)'),
            hovermode='closest',
            template='plotly_white'
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({'success': True, 'chart': chart_json})
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/<int:product_id>/export')
def export_price_history(product_id):
    """API endpoint to export price history as CSV."""
    try:
        format_type = request.args.get('format', 'csv')
        result = tracker.export_price_history(product_id, format=format_type)
        
        if not result['success']:
            return jsonify(result)
        
        if format_type == 'csv':
            # Create file-like object
            output = io.StringIO(result['data'])
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=result['filename']
            )
        else:
            return jsonify(result)
    except Exception as e:
        logger.error(f"Error exporting price history: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications')
def get_notifications():
    """API endpoint to get pending notifications."""
    try:
        notifications = tracker.db.get_pending_notifications()
        return jsonify({'success': True, 'notifications': notifications})
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications/process', methods=['POST'])
def process_notifications():
    """API endpoint to process pending notifications."""
    try:
        result = tracker.process_notifications()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing notifications: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-all', methods=['POST'])
def check_all_products():
    """API endpoint to check all product prices."""
    try:
        result = tracker.check_all_products()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error checking all products: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-scraping', methods=['POST'])
def test_scraping():
    """API endpoint to test scraping for a URL."""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        result = tracker.test_scraping(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing scraping: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """API endpoint to test email configuration."""
    try:
        result = tracker.test_email_configuration()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing email: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get application statistics."""
    try:
        stats = tracker.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

def main():
    """Main function to run the dashboard."""
    print("🌐 Starting Price Tracker Dashboard...")
    print(f"Dashboard will be available at: http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    
    app.run(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=Config.DASHBOARD_DEBUG
    )

if __name__ == "__main__":
    main()
