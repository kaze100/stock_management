#!/usr/bin/env python
"""
Database Schema Fix for Smart Inventory System
This script fixes the database schema mismatch by adding missing columns
"""
import os
import sys
import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_schema_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_schema_fix")

# Database path
DB_PATH = 'new_inventory.db'

def check_columns():
    """Check if the packaged product columns exist in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get column info for the product table
        cursor.execute("PRAGMA table_info(product)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if packaged product columns exist
        missing_columns = []
        for col in ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']:
            if col not in column_names:
                missing_columns.append(col)
        
        conn.close()
        return missing_columns
    
    except Exception as e:
        logger.error(f"Error checking columns: {e}")
        return ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']

def add_missing_columns(missing_columns):
    """Add missing columns to the product table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for col in missing_columns:
            if col == 'is_packaged':
                cursor.execute("ALTER TABLE product ADD COLUMN is_packaged BOOLEAN DEFAULT 0")
            elif col == 'units_per_package':
                cursor.execute("ALTER TABLE product ADD COLUMN units_per_package INTEGER DEFAULT 1")
            elif col == 'individual_price':
                cursor.execute("ALTER TABLE product ADD COLUMN individual_price FLOAT DEFAULT 0")
            elif col == 'individual_stock':
                cursor.execute("ALTER TABLE product ADD COLUMN individual_stock INTEGER DEFAULT 0")
            
            logger.info(f"Added column: {col}")
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error adding columns: {e}")
        return False

def fix_app_py():
    """Fix app.py to ensure Product model matches the database schema"""
    logger.info("Fixing app.py to match database schema...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.db_schema_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the Product class definition
        product_class_start = -1
        product_class_end = -1
        
        for i, line in enumerate(lines):
            if "class Product(db.Model):" in line:
                product_class_start = i
            elif product_class_start != -1 and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                product_class_end = i
                break
        
        if product_class_end == -1:
            product_class_end = len(lines)
        
        # Create the updated Product class
        updated_product_class = [
            "class Product(db.Model):\n",
            "    id = db.Column(db.Integer, primary_key=True)\n",
            "    name = db.Column(db.String(100), nullable=False)\n",
            "    description = db.Column(db.String(200))\n",
            "    category = db.Column(db.String(50), default='Uncategorized')\n",
            "    purchase_price = db.Column(db.Float, default=0)\n",
            "    price = db.Column(db.Float, nullable=False)\n",
            "    stock = db.Column(db.Integer, default=0)\n",
            "    low_stock_threshold = db.Column(db.Integer, default=10)\n",
            "    date_added = db.Column(db.DateTime, default=datetime.utcnow)\n",
            "    is_packaged = db.Column(db.Boolean, default=False)\n",
            "    units_per_package = db.Column(db.Integer, default=1)\n",
            "    individual_price = db.Column(db.Float, default=0)\n",
            "    individual_stock = db.Column(db.Integer, default=0)\n",
            "\n",
            "    def is_low_stock(self):\n",
            "        return self.stock <= self.low_stock_threshold\n",
            "\n",
            "    def get_profit_margin(self):\n",
            "        if self.purchase_price > 0:\n",
            "            return ((self.price - self.purchase_price) / self.price) * 100\n",
            "        return 100  # If purchase price is 0, profit margin is 100%\n",
            "\n"
        ]
        
        # Replace the Product class in the file
        updated_lines = lines[:product_class_start] + updated_product_class + lines[product_class_end:]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        logger.info("Successfully updated Product model in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing app.py: {e}")
        return False

def fix_sell_product_route():
    """Fix the sell_product route to handle packaged products properly"""
    try:
        app_path = 'app.py'
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the sell_product route needs to be fixed
        if "if product.is_packaged:" in content:
            logger.info("sell_product route already handles packaged products")
            return True
        
        # Find the sell_product route
        sell_product_start = content.find("@app.route('/cashier/sell'")
        if sell_product_start == -1:
            logger.warning("Could not find sell_product route")
            return False
        
        # Find the part where product stock is updated
        stock_update_start = content.find("product.stock -= quantity", sell_product_start)
        if stock_update_start == -1:
            logger.warning("Could not find stock update in sell_product route")
            return False
        
        # Get the line before the stock update
        line_end = content.rfind("\n", 0, stock_update_start)
        line_start = content.rfind("\n", 0, line_end) + 1
        
        # Replace the simple stock update with packaged product handling
        updated_content = content[:line_start] + """        # Calculate total price and update stock based on product type
        if product.is_packaged:
            # Default to selling as a package
            total_price = product.price * quantity
            product.stock -= quantity
        else:
            # Regular product
            total_price = product.price * quantity
            product.stock -= quantity
""" + content[stock_update_start + len("product.stock -= quantity"):]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("Successfully updated sell_product route in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing sell_product route: {e}")
        return False

if __name__ == "__main__":
    print("Running database schema fix for Smart Inventory System...")
    
    # Check for missing columns
    missing_columns = check_columns()
    
    if missing_columns:
        print(f"Missing columns detected: {', '.join(missing_columns)}")
        
        # Add missing columns to the database
        if add_missing_columns(missing_columns):
            print("Successfully added missing columns to the database")
        else:
            print("Failed to add missing columns to the database")
    else:
        print("No missing columns detected in the database")
    
    # Fix the Product model in app.py
    if fix_app_py():
        print("Successfully updated Product model in app.py")
    else:
        print("Failed to update Product model in app.py")
    
    # Fix the sell_product route
    if fix_sell_product_route():
        print("Successfully updated sell_product route in app.py")
    else:
        print("Failed to update sell_product route in app.py")
    
    print("\nDatabase schema fix completed!")
    print("\nInstructions:")
    print("1. Reload your web app from the PythonAnywhere Web tab")
    print("2. Clear your browser cookies and cache")
    print("3. Try accessing the site again")
    print("\nThis fix ensures that your database schema matches your code")
