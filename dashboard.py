"""
Web dashboard for the E-commerce Price Tracker & Notifier application.
Provides HTML interface for managing products, viewing statistics, and visualizing price history.
"""
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.utils
import pandas as pd
from price_tracker import PriceTracker
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)
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

@app.route('/test')
def test_page():
    """Test page for debugging."""
    return send_file('test_dashboard.html')

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

def create_templates():
    """Create HTML templates for the dashboard."""
    
    # Create templates directory
    import os
    os.makedirs('templates', exist_ok=True)
    
    # Dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Price Tracker & Notifier</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .card { margin-bottom: 20px; }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .price-drop { color: #dc3545; }
        .price-rise { color: #28a745; }
        .loading { display: none; }
        .chart-container { height: 400px; }
        .notification-badge { position: absolute; top: -5px; right: -5px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chart-line"></i> Price Tracker
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text">
                    <i class="fas fa-clock"></i> Last updated: <span id="last-updated">{{ stats.last_check }}</span>
                </span>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ stats.database_stats.total_products }}</h3>
                        <p class="mb-0">Active Products</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ stats.database_stats.products_with_drops }}</h3>
                        <p class="mb-0">Products with Drops</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ stats.database_stats.total_notifications }}</h3>
                        <p class="mb-0">Notifications Sent</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <h3>{{ "%.1f"|format(stats.database_stats.avg_drop_percent) }}%</h3>
                        <p class="mb-0">Avg Drop</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cogs"></i> Actions</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary me-2" onclick="addProductModal()">
                            <i class="fas fa-plus"></i> Add Product
                        </button>
                        <button class="btn btn-success me-2" onclick="checkAllProducts()">
                            <i class="fas fa-sync"></i> Check All Prices
                        </button>
                        <button class="btn btn-warning me-2" onclick="processNotifications()">
                            <i class="fas fa-envelope"></i> Process Notifications
                            <span class="badge bg-danger notification-badge" id="notification-count">{{ stats.pending_notifications }}</span>
                        </button>
                        <button class="btn btn-info me-2" onclick="testScrapingModal()">
                            <i class="fas fa-vial"></i> Test Scraping
                        </button>
                        <button class="btn btn-secondary" onclick="testEmailModal()">
                            <i class="fas fa-envelope-open"></i> Test Email
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Products Table -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Tracked Products</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Product Name</th>
                                        <th>Current Price</th>
                                        <th>Threshold</th>
                                        <th>Site</th>
                                        <th>Last Checked</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="products-table">
                                    {% for product in products %}
                                    <tr data-product-id="{{ product.id }}">
                                        <td>{{ product.product_name }}</td>
                                        <td class="current-price">₹{{ "%.2f"|format(product.current_price or 0) }}</td>
                                        <td>₹{{ "%.2f"|format(product.threshold_price) }}</td>
                                        <td><span class="badge bg-primary">{{ product.site_type }}</span></td>
                                        <td>{{ product.last_checked }}</td>
                                        <td>
                                            {% if product.is_active %}
                                            <span class="badge bg-success">Active</span>
                                            {% else %}
                                            <span class="badge bg-secondary">Inactive</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary" onclick="checkProduct({{ product.id }})">
                                                <i class="fas fa-sync"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-info" onclick="viewChart({{ product.id }})">
                                                <i class="fas fa-chart-line"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-success" onclick="exportHistory({{ product.id }})">
                                                <i class="fas fa-download"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct({{ product.id }})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Product Modal -->
    <div class="modal fade" id="addProductModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Product</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addProductForm">
                        <div class="mb-3">
                            <label class="form-label">Product URL</label>
                            <input type="url" class="form-control" id="productUrl" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Threshold Price (₹)</label>
                            <input type="number" class="form-control" id="thresholdPrice" step="0.01" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Product Name (Optional)</label>
                            <input type="text" class="form-control" id="productName">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitAddProduct()">Add Product</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Chart Modal -->
    <div class="modal fade" id="chartModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Price History Chart</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="priceChart" class="chart-container"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Test Scraping Modal -->
    <div class="modal fade" id="testScrapingModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Test Scraping</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Product URL</label>
                        <input type="url" class="form-control" id="testUrl" placeholder="Enter Amazon or Flipkart URL">
                    </div>
                    <div id="testResults"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="testScraping()">Test</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Test Email Modal -->
    <div class="modal fade" id="testEmailModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Test Email Configuration</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="emailTestResults"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="testEmail()">Test Email</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Global variables
        let currentProductId = null;

        // Utility functions
        function showLoading(elementId) {
            document.getElementById(elementId).style.display = 'block';
        }

        function hideLoading(elementId) {
            document.getElementById(elementId).style.display = 'none';
        }

        function showAlert(message, type = 'info') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }

        // Modal functions
        function addProductModal() {
            new bootstrap.Modal(document.getElementById('addProductModal')).show();
        }

        function testScrapingModal() {
            new bootstrap.Modal(document.getElementById('testScrapingModal')).show();
        }

        function testEmailModal() {
            new bootstrap.Modal(document.getElementById('testEmailModal')).show();
        }

        // API functions
        async function submitAddProduct() {
            const url = document.getElementById('productUrl').value;
            const thresholdPrice = document.getElementById('thresholdPrice').value;
            const productName = document.getElementById('productName').value;

            try {
                const response = await fetch('/api/products', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, threshold_price: thresholdPrice, product_name: productName })
                });

                const result = await response.json();
                
                if (result.success) {
                    showAlert('Product added successfully!', 'success');
                    location.reload();
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function checkProduct(productId) {
            try {
                const response = await fetch(`/api/products/${productId}/check`, { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    const row = document.querySelector(`tr[data-product-id="${productId}"]`);
                    const priceCell = row.querySelector('.current-price');
                    priceCell.textContent = `₹${result.new_price.toFixed(2)}`;
                    
                    if (result.price_dropped) {
                        showAlert(`Price drop detected for ${result.product_name}!`, 'success');
                    } else {
                        showAlert(`Price checked for ${result.product_name}`, 'info');
                    }
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function checkAllProducts() {
            try {
                showAlert('Checking all products...', 'info');
                const response = await fetch('/api/check-all', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showAlert(`Checked ${result.products_checked} products. Found ${result.price_drops} price drops.`, 'success');
                    location.reload();
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function processNotifications() {
            try {
                const response = await fetch('/api/notifications/process', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showAlert(`Processed ${result.notifications_processed} notifications. Sent ${result.emails_sent} emails.`, 'success');
                    document.getElementById('notification-count').textContent = '0';
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function viewChart(productId) {
            currentProductId = productId;
            try {
                const response = await fetch(`/api/products/${productId}/chart`);
                const result = await response.json();
                
                if (result.success) {
                    const chartData = JSON.parse(result.chart);
                    Plotly.newPlot('priceChart', chartData.data, chartData.layout);
                    new bootstrap.Modal(document.getElementById('chartModal')).show();
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function exportHistory(productId) {
            try {
                window.open(`/api/products/${productId}/export?format=csv`, '_blank');
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function deleteProduct(productId) {
            if (!confirm('Are you sure you want to stop tracking this product?')) return;
            
            try {
                const response = await fetch(`/api/products/${productId}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    showAlert('Product deactivated successfully!', 'success');
                    location.reload();
                } else {
                    showAlert(`Error: ${result.error}`, 'danger');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'danger');
            }
        }

        async function testScraping() {
            const url = document.getElementById('testUrl').value;
            const resultsDiv = document.getElementById('testResults');
            
            try {
                resultsDiv.innerHTML = '<div class="alert alert-info">Testing scraping...</div>';
                
                const response = await fetch('/api/test-scraping', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = '<div class="alert alert-success"><h6>Test Results:</h6>';
                    if (result.requests_method) {
                        html += `<p><strong>Requests Method:</strong> ✅ Success - ${result.requests_method.product_name} - ₹${result.requests_method.price}</p>`;
                    } else {
                        html += '<p><strong>Requests Method:</strong> ❌ Failed</p>';
                    }
                    if (result.playwright_method) {
                        html += `<p><strong>Playwright Method:</strong> ✅ Success - ${result.playwright_method.product_name} - ₹${result.playwright_method.price}</p>`;
                    } else {
                        html += '<p><strong>Playwright Method:</strong> ❌ Failed</p>';
                    }
                    html += `<p><strong>Recommended Method:</strong> ${result.recommended_method}</p></div>`;
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            }
        }

        async function testEmail() {
            const resultsDiv = document.getElementById('emailTestResults');
            
            try {
                resultsDiv.innerHTML = '<div class="alert alert-info">Testing email configuration...</div>';
                
                const response = await fetch('/api/test-email', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    let html = '<div class="alert alert-success"><h6>Email Test Results:</h6>';
                    html += `<p><strong>Configuration:</strong> ${result.config_valid ? '✅ Valid' : '❌ Invalid'}</p>`;
                    html += `<p><strong>SMTP Connection:</strong> ${result.smtp_connection ? '✅ Success' : '❌ Failed'}</p>`;
                    html += `<p><strong>Authentication:</strong> ${result.authentication ? '✅ Success' : '❌ Failed'}</p>`;
                    html += `<p><strong>Test Email:</strong> ${result.test_email_sent ? '✅ Sent' : '❌ Failed'}</p>`;
                    html += '</div>';
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            }
        }

        // Auto-refresh every 5 minutes
        setInterval(() => {
            location.reload();
        }, 300000);
    </script>
</body>
</html>'''
    
    # Error template
    error_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Price Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body text-center">
                        <h1 class="text-danger"><i class="fas fa-exclamation-triangle"></i></h1>
                        <h3>Oops! Something went wrong</h3>
                        <p class="text-muted">{{ error }}</p>
                        <a href="/" class="btn btn-primary">Go Back to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    # Write templates
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    with open('templates/error.html', 'w', encoding='utf-8') as f:
        f.write(error_html)

def main():
    """Main function to run the dashboard."""
    # Create templates
    create_templates()
    
    print("🌐 Starting Price Tracker Dashboard...")
    print(f"Dashboard will be available at: http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    
    app.run(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=Config.DASHBOARD_DEBUG
    )

if __name__ == "__main__":
    main()
