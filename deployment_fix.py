#!/usr/bin/env python3
"""
Deployment troubleshooting script for Smart Inventory System
This script helps diagnose and fix common deployment issues
"""
import os
import sys
import sqlite3
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deployment_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("deployment_fix")

# Path to the database file - adjust as needed for your deployment environment
DB_PATH = 'instance/new_inventory.db'
PROD_DB_PATH = '/home/renoir0/SmartInventory/instance/new_inventory.db'

def check_environment():
    """Check the environment configuration"""
    logger.info("Checking environment configuration...")
    
    # Check Python version
    python_version = sys.version
    logger.info(f"Python version: {python_version}")
    
    # Check environment variables
    flask_app = os.environ.get('FLASK_APP')
    logger.info(f"FLASK_APP: {flask_app}")
    
    # Check current directory
    current_dir = os.getcwd()
    logger.info(f"Current directory: {current_dir}")
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    logger.info(f"Running in virtual environment: {in_venv}")
    
    return True

def check_database(db_path):
    """Check database structure and fix if needed"""
    logger.info(f"Checking database at {db_path}...")
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        logger.info(f"Found tables: {', '.join(table_names)}")
        
        # Check product table structure
        if 'product' in table_names:
            cursor.execute("PRAGMA table_info(product)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            logger.info(f"Product table columns: {', '.join(column_names)}")
            
            # Check for packaged product columns
            packaged_columns = ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']
            missing_columns = [col for col in packaged_columns if col not in column_names]
            
            if missing_columns:
                logger.warning(f"Missing packaged product columns: {', '.join(missing_columns)}")
                
                # Add missing columns
                for column in missing_columns:
                    if column == 'is_packaged':
                        cursor.execute("ALTER TABLE product ADD COLUMN is_packaged BOOLEAN DEFAULT 0")
                    elif column == 'units_per_package':
                        cursor.execute("ALTER TABLE product ADD COLUMN units_per_package INTEGER DEFAULT 1")
                    elif column == 'individual_price':
                        cursor.execute("ALTER TABLE product ADD COLUMN individual_price FLOAT DEFAULT 0")
                    elif column == 'individual_stock':
                        cursor.execute("ALTER TABLE product ADD COLUMN individual_stock INTEGER DEFAULT 0")
                
                conn.commit()
                logger.info("Added missing packaged product columns")
                
                # Update existing products with default values
                cursor.execute("""
                    UPDATE product 
                    SET 
                        is_packaged = 0,
                        units_per_package = 1,
                        individual_price = price,
                        individual_stock = 0
                    WHERE is_packaged IS NULL
                """)
                conn.commit()
                logger.info("Updated existing products with default values for packaged product columns")
            
            # Check for NULL values in packaged product columns
            for column in packaged_columns:
                if column in column_names:
                    cursor.execute(f"SELECT COUNT(*) FROM product WHERE {column} IS NULL")
                    null_count = cursor.fetchone()[0]
                    if null_count > 0:
                        logger.warning(f"Found {null_count} NULL values in {column} column")
                        
                        # Fix NULL values
                        if column == 'is_packaged':
                            cursor.execute("UPDATE product SET is_packaged = 0 WHERE is_packaged IS NULL")
                        elif column == 'units_per_package':
                            cursor.execute("UPDATE product SET units_per_package = 1 WHERE units_per_package IS NULL")
                        elif column == 'individual_price':
                            cursor.execute("UPDATE product SET individual_price = price WHERE individual_price IS NULL")
                        elif column == 'individual_stock':
                            cursor.execute("UPDATE product SET individual_stock = 0 WHERE individual_stock IS NULL")
                        
                        conn.commit()
                        logger.info(f"Fixed NULL values in {column} column")
        else:
            logger.error("Product table not found in database")
            return False
        
        conn.close()
        logger.info("Database check completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False

def fix_templates():
    """Fix template files for packaged products"""
    logger.info("Fixing template files for packaged products...")
    
    try:
        # Fix cashier_dashboard.html
        cashier_dashboard_path = os.path.join('templates', 'cashier_dashboard.html')
        if os.path.exists(cashier_dashboard_path):
            # Create backup
            backup_path = f"{cashier_dashboard_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(cashier_dashboard_path, backup_path)
            logger.info(f"Created backup of cashier_dashboard.html: {backup_path}")
            
            # Read the file
            with open(cashier_dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if the file already has the packaged product fields
            if 'id="sale_type"' in content:
                logger.info("cashier_dashboard.html already has packaged product fields")
            else:
                logger.info("Reverting cashier_dashboard.html to basic version")
                
                # Create a simplified version without packaged product fields
                with open(cashier_dashboard_path, 'w', encoding='utf-8') as f:
                    f.write('''{% extends "base.html" %}

{% block title %}{{ _('Cashier Dashboard') }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>{{ _('Cashier Dashboard') }}</h1>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card mb-4">
                <div class="card-header">
                    <h5>{{ _('Record Sale') }}</h5>
                </div>
                <div class="card-body">
                    <form action="{{ url_for('sell_product') }}" method="post">
                        <div class="mb-3">
                            <label for="product_id" class="form-label">{{ _('Select Product') }}</label>
                            <select class="form-select" id="product_id" name="product_id" required>
                                <option value="">{{ _('-- Select a product --') }}</option>
                                {% for product in products %}
                                <option value="{{ product.id }}">
                                    {{ product.name }} - {{ _('Price') }}: {{ product.price }} - {{ _('Stock') }}: {{ product.stock }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="quantity" class="form-label">{{ _('Quantity') }}</label>
                            <input type="number" class="form-control" id="quantity" name="quantity" min="1" value="1" required>
                        </div>
                        <button type="submit" class="btn btn-primary">{{ _('Record Sale') }}</button>
                    </form>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h5>{{ _('Search Products') }}</h5>
                </div>
                <div class="card-body">
                    <form action="{{ url_for('cashier_dashboard') }}" method="get">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" name="search" placeholder="{{ _('Search by product name') }}" value="{{ search_query }}">
                            <button class="btn btn-outline-secondary" type="submit">{{ _('Search') }}</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>{{ _('Today\'s Sales') }}</h5>
                </div>
                <div class="card-body">
                    <h6>{{ _('Total Revenue') }}: {{ total_revenue }}</h6>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>{{ _('Product') }}</th>
                                <th>{{ _('Quantity') }}</th>
                                <th>{{ _('Total') }}</th>
                                <th>{{ _('Time') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sale in today_sales %}
                            <tr>
                                <td>{{ sale.product.name }}</td>
                                <td>{{ sale.quantity }}</td>
                                <td>{{ sale.total_price }}</td>
                                <td>{{ sale.date_sold.strftime('%H:%M') }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    <a href="{{ url_for('view_cashier_sales') }}" class="btn btn-outline-primary">{{ _('View All Sales') }}</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
                logger.info("Fixed cashier_dashboard.html")
        
        # Fix add_product.html and edit_product.html
        for template_file in ['add_product.html', 'edit_product.html']:
            template_path = os.path.join('templates', template_file)
            if os.path.exists(template_path):
                # Create backup
                backup_path = f"{template_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(template_path, backup_path)
                logger.info(f"Created backup of {template_file}: {backup_path}")
                
                # Read the file
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if the file already has the packaged product fields
                if 'id="is_packaged"' in content:
                    logger.info(f"{template_file} already has packaged product fields")
                    
                    # Create a simplified version without packaged product fields
                    if template_file == 'add_product.html':
                        with open(template_path, 'w', encoding='utf-8') as f:
                            f.write('''{% extends "base.html" %}

{% block title %}{{ _('Add Product') }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>{{ _('Add Product') }}</h1>
    
    <div class="card">
        <div class="card-body">
            <form action="{{ url_for('add_product') }}" method="post">
                <div class="mb-3">
                    <label for="name" class="form-label">{{ _('Product Name') }}</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">{{ _('Description') }}</label>
                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">{{ _('Category') }}</label>
                    <input type="text" class="form-control" id="category" name="category" value="Uncategorized">
                </div>
                <div class="mb-3">
                    <label for="purchase_price" class="form-label">{{ _('Purchase Price') }}</label>
                    <input type="number" class="form-control" id="purchase_price" name="purchase_price" min="0" step="0.01" value="0" required>
                </div>
                <div class="mb-3">
                    <label for="price" class="form-label">{{ _('Selling Price') }}</label>
                    <input type="number" class="form-control" id="price" name="price" min="0" step="0.01" required>
                </div>
                <div class="mb-3">
                    <label for="stock" class="form-label">{{ _('Initial Stock') }}</label>
                    <input type="number" class="form-control" id="stock" name="stock" min="0" value="0" required>
                </div>
                <div class="mb-3">
                    <label for="low_stock_threshold" class="form-label">{{ _('Low Stock Threshold') }}</label>
                    <input type="number" class="form-control" id="low_stock_threshold" name="low_stock_threshold" min="1" value="10" required>
                </div>
                <button type="submit" class="btn btn-primary">{{ _('Add Product') }}</button>
                <a href="{{ url_for('manage_products') }}" class="btn btn-secondary">{{ _('Cancel') }}</a>
            </form>
        </div>
    </div>
</div>
{% endblock %}''')
                    elif template_file == 'edit_product.html':
                        with open(template_path, 'w', encoding='utf-8') as f:
                            f.write('''{% extends "base.html" %}

{% block title %}{{ _('Edit Product') }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>{{ _('Edit Product') }}</h1>
    
    <div class="card">
        <div class="card-body">
            <form action="{{ url_for('edit_product', product_id=product.id) }}" method="post">
                <div class="mb-3">
                    <label for="name" class="form-label">{{ _('Product Name') }}</label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ product.name }}" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">{{ _('Description') }}</label>
                    <textarea class="form-control" id="description" name="description" rows="3">{{ product.description }}</textarea>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">{{ _('Category') }}</label>
                    <input type="text" class="form-control" id="category" name="category" value="{{ product.category }}">
                </div>
                <div class="mb-3">
                    <label for="purchase_price" class="form-label">{{ _('Purchase Price') }}</label>
                    <input type="number" class="form-control" id="purchase_price" name="purchase_price" min="0" step="0.01" value="{{ product.purchase_price }}" required>
                </div>
                <div class="mb-3">
                    <label for="price" class="form-label">{{ _('Selling Price') }}</label>
                    <input type="number" class="form-control" id="price" name="price" min="0" step="0.01" value="{{ product.price }}" required>
                </div>
                <div class="mb-3">
                    <label for="stock" class="form-label">{{ _('Current Stock') }}</label>
                    <input type="number" class="form-control" id="stock" name="stock" min="0" value="{{ product.stock }}" required>
                </div>
                <div class="mb-3">
                    <label for="low_stock_threshold" class="form-label">{{ _('Low Stock Threshold') }}</label>
                    <input type="number" class="form-control" id="low_stock_threshold" name="low_stock_threshold" min="1" value="{{ product.low_stock_threshold }}" required>
                </div>
                <button type="submit" class="btn btn-primary">{{ _('Update Product') }}</button>
                <a href="{{ url_for('manage_products') }}" class="btn btn-secondary">{{ _('Cancel') }}</a>
            </form>
        </div>
    </div>
</div>
{% endblock %}''')
                    logger.info(f"Fixed {template_file}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing templates: {str(e)}")
        return False

def fix_app_py():
    """Fix app.py to remove packaged products functionality"""
    logger.info("Fixing app.py to remove packaged products functionality...")
    
    app_path = 'app.py'
    
    try:
        # Create backup
        backup_path = f"{app_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(app_path, backup_path)
        logger.info(f"Created backup of app.py: {backup_path}")
        
        # Read the file
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Modify the file to remove packaged products functionality
        modified_lines = []
        in_product_class = False
        skip_packaged_fields = False
        
        for line in lines:
            if 'class Product(db.Model):' in line:
                in_product_class = True
                modified_lines.append(line)
            elif in_product_class and '# New fields for package handling' in line:
                skip_packaged_fields = True
                # Skip this line
            elif in_product_class and skip_packaged_fields and line.strip() == '':
                skip_packaged_fields = False
                modified_lines.append(line)
            elif skip_packaged_fields:
                # Skip packaged product fields
                pass
            elif 'def get_total_units(self):' in line:
                # Skip this method entirely
                while not line.strip().startswith('def ') and not line.strip().startswith('class '):
                    if lines.index(line) < len(lines) - 1:
                        line = lines[lines.index(line) + 1]
                    else:
                        break
                modified_lines.append(line)
            elif 'if product.is_packaged:' in line:
                # Replace packaged product handling with simple code
                modified_lines.append('        # Check if enough stock is available\n')
                modified_lines.append('        if product.stock < quantity:\n')
                modified_lines.append('            flash(_("Not enough stock available. Only {0} units left.", product.stock), "danger")\n')
                modified_lines.append('            return redirect(url_for("cashier_dashboard"))\n')
                modified_lines.append('        \n')
                modified_lines.append('        # Calculate total price\n')
                modified_lines.append('        total_price = product.price * quantity\n')
                modified_lines.append('        \n')
                modified_lines.append('        # Create sale record\n')
                modified_lines.append('        sale = Sale(\n')
                modified_lines.append('            product_id=product_id,\n')
                modified_lines.append('            quantity=quantity,\n')
                modified_lines.append('            total_price=total_price,\n')
                modified_lines.append('            cashier_id=current_user.id\n')
                modified_lines.append('        )\n')
                modified_lines.append('        \n')
                modified_lines.append('        # Update product stock\n')
                modified_lines.append('        product.stock -= quantity\n')
                
                # Skip until we're past this block
                skip_block = True
                block_indent = len(line) - len(line.lstrip())
                while skip_block:
                    if lines.index(line) < len(lines) - 1:
                        line = lines[lines.index(line) + 1]
                        if line.strip() and len(line) - len(line.lstrip()) <= block_indent:
                            skip_block = False
                            modified_lines.append(line)
                    else:
                        skip_block = False
            elif 'products = Product.query.filter(' in line and 'Product.individual_stock > 0' in line:
                # Replace with simple filter
                modified_lines.append('    products = Product.query.filter(Product.stock > 0).all()\n')
                
                # Skip until we're past this block
                skip_block = True
                block_indent = len(line) - len(line.lstrip())
                while skip_block:
                    if lines.index(line) < len(lines) - 1:
                        line = lines[lines.index(line) + 1]
                        if line.strip() and len(line) - len(line.lstrip()) <= block_indent:
                            skip_block = False
                            modified_lines.append(line)
                    else:
                        skip_block = False
            else:
                modified_lines.append(line)
        
        # Write the modified file
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        logger.info("Fixed app.py to remove packaged products functionality")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing app.py: {str(e)}")
        return False

def run_diagnostics_and_fix():
    """Run diagnostics and fix issues"""
    logger.info("Starting deployment diagnostics and fixes...")
    
    # Run diagnostics
    check_environment()
    
    # Check and fix database
    db_path = PROD_DB_PATH if os.path.exists(PROD_DB_PATH) else DB_PATH
    db_result = check_database(db_path)
    
    # Fix templates
    templates_result = fix_templates()
    
    # Fix app.py
    app_result = fix_app_py()
    
    # Print summary
    logger.info("\n--- Fix Summary ---")
    logger.info(f"Database Fix: {'SUCCESS' if db_result else 'FAILED'}")
    logger.info(f"Templates Fix: {'SUCCESS' if templates_result else 'FAILED'}")
    logger.info(f"App.py Fix: {'SUCCESS' if app_result else 'FAILED'}")
    
    if db_result and templates_result and app_result:
        logger.info("\nAll fixes applied successfully!")
        logger.info("\nInstructions:")
        logger.info("1. Reload your web app from the PythonAnywhere Web tab")
        logger.info("2. Clear your browser cookies and cache")
        logger.info("3. Try accessing the site again")
        logger.info("\nThis fix removes the packaged products feature while preserving all your data")
        return True
    else:
        logger.error("\nSome fixes failed. Please check the logs for details.")
        return False

if __name__ == "__main__":
    run_diagnostics_and_fix()
