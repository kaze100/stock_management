"""
Smart Inventory System - PythonAnywhere Fix Script
-------------------------------------------------
This script fixes common issues when deploying to PythonAnywhere:
1. Flask-Babel compatibility issues
2. Database initialization
3. Template errors with low_stock_products
4. View_sales template escape function error
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# Configuration
DB_PATH = 'new_inventory.db'  # Default path, will be searched for

def find_database():
    """Find the database file on PythonAnywhere."""
    global DB_PATH
    
    print("Looking for database file...")
    if os.path.exists(DB_PATH):
        print(f"Found database at {DB_PATH}")
        return True
        
    # Try to find the database file
    possible_paths = [
        'new_inventory.db',
        'instance/new_inventory.db',
        '../new_inventory.db',
        '../instance/new_inventory.db',
        '/home/renoir0/SmartInventory/new_inventory.db',
        '/home/renoir0/new_inventory.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found database at {path}")
            DB_PATH = path
            return True
    
    print("Database file not found. Will create a new one.")
    DB_PATH = 'new_inventory.db'
    return False

def fix_babel_issue():
    """Fix Flask-Babel compatibility issues."""
    print("\nFixing Flask-Babel compatibility issues...")
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found!")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace localeselector with get_locale
    if '@babel.localeselector' in content:
        content = content.replace('@babel.localeselector', '@babel.localeselector_func')
        
        # Add compatibility function
        babel_fix = """
# Compatibility fix for newer Flask-Babel versions
try:
    # For newer Flask-Babel versions
    babel.localeselector_func = babel.get_locale
except AttributeError:
    # For older Flask-Babel versions
    babel.localeselector_func = babel.localeselector
"""
        # Insert the compatibility fix after the babel initialization
        babel_init_pos = content.find('babel = Babel(app)')
        if babel_init_pos > 0:
            insert_pos = content.find('\n', babel_init_pos) + 1
            content = content[:insert_pos] + babel_fix + content[insert_pos:]
        
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print("Fixed Flask-Babel compatibility issue.")
        return True
    else:
        print("No Flask-Babel compatibility issues found.")
        return True

def fix_admin_dashboard_template():
    """Fix the admin_dashboard template for low_stock_products."""
    print("\nFixing admin_dashboard template...")
    
    template_path = 'templates/admin_dashboard.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the template uses low_stock_products as a list
    if '{% for product in low_stock_products %}' in content:
        # Modify the admin_dashboard.html template to handle both list and int
        modified_content = content.replace(
            '{% for product in low_stock_products %}',
            '{% if low_stock_products is iterable and low_stock_products is not string %}{% for product in low_stock_products %}'
        )
        
        # Add closing tag for the if statement
        modified_content = modified_content.replace(
            '{% endfor %}',
            '{% endfor %}{% else %}<tr><td colspan="5">{{ _("No low stock products") }}</td></tr>{% endif %}'
        )
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print("Fixed admin_dashboard template.")
        return True
    else:
        print("No issues found in admin_dashboard template.")
        return True

def fix_view_sales_template():
    """Fix the view_sales template escape function issue."""
    print("\nFixing view_sales template...")
    
    template_path = 'templates/view_sales.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the escape function issue
    if "escape('js')" in content:
        modified_content = content.replace(
            "escape('js')",
            "escape"
        )
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print("Fixed view_sales template.")
        return True
    else:
        print("No issues found in view_sales template.")
        return True

def initialize_database():
    """Initialize the database with tables and default data."""
    print("\nInitializing database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create user table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # Create product table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT,
            low_stock_threshold INTEGER DEFAULT 10,
            purchase_price REAL DEFAULT 0
        )
        ''')
        
        # Create sale table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date_sold TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            cashier_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES product (id),
            FOREIGN KEY (cashier_id) REFERENCES user (id)
        )
        ''')
        
        # Add admin user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'renoir01'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('renoir01', generate_password_hash('Renoir@654'), 'admin')
            )
            print("Created admin user 'renoir01' with password 'Renoir@654'")
        
        # Add cashier user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'epi'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('epi', generate_password_hash('Epi@654'), 'cashier')
            )
            print("Created cashier user 'epi' with password 'Epi@654'")
        
        # Add some sample products if the product table is empty
        cursor.execute("SELECT COUNT(*) FROM product")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ('Laptop', 'High-performance laptop', 1200.00, 15, 'Electronics', 5, 900.00),
                ('Smartphone', 'Latest model smartphone', 800.00, 25, 'Electronics', 8, 600.00),
                ('Headphones', 'Noise-cancelling headphones', 150.00, 30, 'Electronics', 10, 90.00),
                ('Desk Chair', 'Ergonomic office chair', 250.00, 10, 'Furniture', 3, 150.00),
                ('Coffee Maker', 'Automatic coffee machine', 120.00, 8, 'Appliances', 5, 75.00)
            ]
            
            cursor.executemany(
                "INSERT INTO product (name, description, price, stock, category, low_stock_threshold, purchase_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                sample_products
            )
            print(f"Added {len(sample_products)} sample products")
        
        # Add some sample sales if the sale table is empty
        cursor.execute("SELECT COUNT(*) FROM sale")
        if cursor.fetchone()[0] == 0:
            # Get admin and cashier IDs
            cursor.execute("SELECT id FROM user WHERE role = 'admin' LIMIT 1")
            admin_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM user WHERE role = 'cashier' LIMIT 1")
            cashier_id = cursor.fetchone()[0]
            
            # Get product IDs
            cursor.execute("SELECT id FROM product")
            product_ids = [row[0] for row in cursor.fetchall()]
            
            if product_ids:
                # Create sample sales for the past week
                today = datetime.now()
                sample_sales = []
                
                for i in range(7):
                    sale_date = today - timedelta(days=i)
                    for product_id in product_ids[:3]:  # Use first 3 products
                        quantity = i % 3 + 1  # 1, 2, or 3 items
                        
                        # Get product price
                        cursor.execute("SELECT price FROM product WHERE id = ?", (product_id,))
                        price = cursor.fetchone()[0]
                        
                        total_price = price * quantity
                        user_id = admin_id if i % 2 == 0 else cashier_id
                        
                        sample_sales.append((
                            product_id, 
                            quantity, 
                            total_price, 
                            sale_date.strftime('%Y-%m-%d %H:%M:%S'), 
                            user_id
                        ))
                
                cursor.executemany(
                    "INSERT INTO sale (product_id, quantity, total_price, date_sold, cashier_id) VALUES (?, ?, ?, ?, ?)",
                    sample_sales
                )
                print(f"Added {len(sample_sales)} sample sales")
        
        conn.commit()
        print("Database initialization completed successfully.")
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Database initialization failed: {str(e)}")
        return False
    
    finally:
        conn.close()

def fix_app_py_for_low_stock():
    """Fix the admin_dashboard route in app.py to ensure low_stock_products is a list."""
    print("\nFixing app.py for low_stock_products...")
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found!")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the admin_dashboard function
    admin_dashboard_start = content.find("def admin_dashboard():")
    if admin_dashboard_start == -1:
        print("Could not find admin_dashboard function in app.py")
        return False
    
    # Find where low_stock_products is defined
    low_stock_line_start = content.find("low_stock_products", admin_dashboard_start)
    if low_stock_line_start == -1:
        print("Could not find low_stock_products in admin_dashboard function")
        return False
    
    # Get the line with low_stock_products
    line_end = content.find("\n", low_stock_line_start)
    low_stock_line = content[low_stock_line_start:line_end]
    
    # Check if it's already using filter and all()
    if "filter" in low_stock_line and ".all()" in low_stock_line:
        print("low_stock_products is already correctly defined as a list")
        return True
    
    # Replace the line to ensure it returns a list
    modified_content = content.replace(
        low_stock_line,
        "low_stock_products = Product.query.filter(Product.stock <= Product.low_stock_threshold).all()"
    )
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed app.py to ensure low_stock_products is a list")
    return True

def main():
    """Run all fixes for PythonAnywhere deployment."""
    print("=== Smart Inventory System - PythonAnywhere Fix Script ===")
    
    # Find the database
    find_database()
    
    # Fix Flask-Babel compatibility issues
    fix_babel_issue()
    
    # Fix admin_dashboard template
    fix_admin_dashboard_template()
    
    # Fix view_sales template
    fix_view_sales_template()
    
    # Fix app.py for low_stock_products
    fix_app_py_for_low_stock()
    
    # Initialize the database
    initialize_database()
    
    print("\n=== All fixes completed ===")
    print("Your Smart Inventory System should now work correctly on PythonAnywhere.")
    print("If you still encounter issues, please check the error logs.")

if __name__ == "__main__":
    main()
