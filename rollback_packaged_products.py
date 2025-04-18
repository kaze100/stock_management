#!/usr/bin/env python
"""
Rollback script for packaged products feature
This script temporarily disables the packaged products feature to restore functionality
"""
import os
import sys
import logging
import sqlite3
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rollback.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rollback")

# Path to the database file - adjust as needed for your deployment environment
DB_PATH = 'instance/inventory.db'
PROD_DB_PATH = '/home/renoir0/SmartInventory/instance/inventory.db'

def rollback_app_py():
    """Modify app.py to disable packaged products feature"""
    logger.info("Rolling back app.py to disable packaged products feature...")
    
    app_path = 'app.py'
    backup_path = f'app.py.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    try:
        # Create backup
        shutil.copy2(app_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        # Read the file
        with open(app_path, 'r') as f:
            lines = f.readlines()
        
        # Modify the Product class
        modified_lines = []
        in_product_class = False
        skip_packaged_fields = False
        
        for line in lines:
            if 'class Product(db.Model):' in line:
                in_product_class = True
                modified_lines.append(line)
            elif in_product_class and '# New fields for package handling' in line:
                skip_packaged_fields = True
                modified_lines.append('    # Packaged products feature temporarily disabled\n')
            elif in_product_class and skip_packaged_fields and line.strip() == '':
                skip_packaged_fields = False
                modified_lines.append(line)
            elif in_product_class and 'def is_low_stock(self):' in line:
                in_product_class = False
                skip_packaged_fields = False
                modified_lines.append('    def is_low_stock(self):\n')
                modified_lines.append('        return self.stock <= self.low_stock_threshold\n')
            elif in_product_class and 'def get_total_units(self):' in line:
                # Skip this method entirely
                skip_method = True
                while skip_method and lines.index(line) < len(lines) - 1:
                    line = lines[lines.index(line) + 1]
                    if 'def ' in line or 'class ' in line:
                        skip_method = False
                        modified_lines.append(line)
            elif 'if product.is_packaged:' in line:
                # Replace packaged product handling with simple code
                modified_lines.append('        # Packaged products feature temporarily disabled\n')
                modified_lines.append('        if product.stock < quantity:\n')
                modified_lines.append('            flash(_("Not enough stock available. Only {0} units left.", product.stock), "danger")\n')
                modified_lines.append('            return redirect(url_for("cashier_dashboard"))\n')
                modified_lines.append('        \n')
                modified_lines.append('        # Calculate total price\n')
                modified_lines.append('        total_price = product.price * quantity\n')
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
            elif 'db.or_(' in line and 'Product.individual_stock > 0' in line:
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
        with open(app_path, 'w') as f:
            f.writelines(modified_lines)
        
        logger.info("Successfully rolled back app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error rolling back app.py: {e}")
        return False

def main():
    """Main function to rollback packaged products feature"""
    logger.info("Starting rollback of packaged products feature...")
    
    # Rollback app.py
    if rollback_app_py():
        logger.info("Rollback completed successfully")
        print("Rollback completed successfully. Please reload your web app.")
    else:
        logger.error("Rollback failed")
        print("Rollback failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
