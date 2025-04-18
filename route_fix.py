#!/usr/bin/env python
"""
Route Fix for Smart Inventory System
This script fixes the missing route issue in the application
"""
import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("route_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("route_fix")

def fix_base_template():
    """Fix the base template to remove references to missing routes"""
    logger.info("Fixing base template...")
    
    template_path = os.path.join('templates', 'base.html')
    backup_path = f"{template_path}.route_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(template_path):
            shutil.copy2(template_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the template file
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the reference to view_sales with a valid route
        if "url_for('view_sales')" in content:
            # Replace with admin_dashboard for admin users
            content = content.replace(
                "<a href=\"{{ url_for('view_sales') }}\" class=\"nav-link {% if request.endpoint == 'view_sales' %}active{% endif %}\">",
                "<a href=\"{{ url_for('admin_dashboard') }}\" class=\"nav-link {% if request.endpoint == 'admin_dashboard' %}active{% endif %}\">"
            )
            logger.info("Replaced view_sales route with admin_dashboard")
        
        # Write the updated content back to the template file
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Successfully fixed base template")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing base template: {e}")
        return False

def add_missing_route():
    """Add the missing view_sales route to app.py"""
    logger.info("Adding missing view_sales route to app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.route_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find a good place to add the new route
        # Let's add it after the delete_product route
        delete_product_end = content.find("@app.route('/admin/products/delete/", 0)
        if delete_product_end == -1:
            logger.warning("Could not find delete_product route")
            return False
        
        # Find the end of the delete_product function
        next_route_start = content.find("@app.route", delete_product_end + 1)
        if next_route_start == -1:
            next_route_start = content.find("@app.errorhandler", delete_product_end + 1)
            if next_route_start == -1:
                logger.warning("Could not find end of delete_product function")
                return False
        
        # Add the view_sales route
        view_sales_route = """
@app.route('/admin/sales')
@login_required
def view_sales():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('login'))
    
    # Get all sales
    sales = Sale.query.order_by(Sale.date_sold.desc()).all()
    
    # Calculate total revenue
    total_revenue = sum(sale.total_price for sale in sales)
    
    return render_template(
        'view_sales.html',
        sales=sales,
        total_revenue=total_revenue
    )

"""
        
        # Insert the new route
        updated_content = content[:next_route_start] + view_sales_route + content[next_route_start:]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("Successfully added view_sales route to app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error adding view_sales route: {e}")
        return False

def create_view_sales_template():
    """Create a view_sales.html template"""
    logger.info("Creating view_sales.html template...")
    
    template_path = os.path.join('templates', 'view_sales.html')
    
    try:
        # Check if the template already exists
        if os.path.exists(template_path):
            logger.info("view_sales.html template already exists")
            return True
        
        # Create the template
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""{% extends 'base.html' %}

{% block title %}{{ _('Sales Report') }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>{{ _('Sales Report') }}</h2>
    
    <div class="card mb-4">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">{{ _('Total Revenue') }}: {{ total_revenue|round(2) }} RWF</h5>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header bg-secondary text-white">
            <h5 class="mb-0">{{ _('All Sales') }}</h5>
        </div>
        <div class="card-body">
            {% if sales %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>{{ _('ID') }}</th>
                            <th>{{ _('Product') }}</th>
                            <th>{{ _('Quantity') }}</th>
                            <th>{{ _('Total Price') }}</th>
                            <th>{{ _('Cashier') }}</th>
                            <th>{{ _('Date') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sale in sales %}
                        <tr>
                            <td>{{ sale.id }}</td>
                            <td>{{ sale.product.name }}</td>
                            <td>{{ sale.quantity }}</td>
                            <td>{{ sale.total_price|round(2) }} RWF</td>
                            <td>{{ sale.cashier.username }}</td>
                            <td>{{ sale.date_sold.strftime('%Y-%m-%d %H:%M') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="alert alert-info">
                {{ _('No sales records found.') }}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
""")
        
        logger.info("Successfully created view_sales.html template")
        return True
    
    except Exception as e:
        logger.error(f"Error creating view_sales.html template: {e}")
        return False

if __name__ == "__main__":
    print("Running route fix for Smart Inventory System...")
    
    # Fix the base template
    if fix_base_template():
        print("Successfully fixed base template")
    else:
        print("Failed to fix base template")
    
    # Add the missing route
    if add_missing_route():
        print("Successfully added view_sales route to app.py")
    else:
        print("Failed to add view_sales route to app.py")
    
    # Create the view_sales template
    if create_view_sales_template():
        print("Successfully created view_sales.html template")
    else:
        print("Failed to create view_sales.html template")
    
    print("\nRoute fix completed!")
    print("\nInstructions:")
    print("1. Restart the Flask server if it's running")
    print("2. Try accessing the site at http://127.0.0.1:5000")
    print("3. Login as admin to test the new Sales Report page")
