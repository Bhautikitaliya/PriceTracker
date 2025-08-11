// Price Tracker Dashboard JavaScript

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
    alertDiv.className = `alert alert-${type} alert-dismissible fade show fade-in`;
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

// Initialize tooltips and other Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
