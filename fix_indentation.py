#!/usr/bin/env python
"""
Fix Indentation Error in app.py
This script fixes the indentation error in the is_low_stock method
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
        logging.FileHandler("fix_indentation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_indentation")

def fix_app_py():
    """Fix indentation error in app.py"""
    logger.info("Fixing indentation error in app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.indentation_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the Product class definition
        product_class_start = -1
        for i, line in enumerate(lines):
            if "class Product(db.Model):" in line:
                product_class_start = i
                break
        
        if product_class_start == -1:
            logger.warning("Could not find Product class definition")
            return False
        
        # Find the is_low_stock method
        is_low_stock_start = -1
        for i in range(product_class_start, len(lines)):
            if "def is_low_stock" in lines[i]:
                is_low_stock_start = i
                break
        
        if is_low_stock_start == -1:
            logger.warning("Could not find is_low_stock method")
            return False
        
        # Fix the indentation
        fixed_lines = []
        for i, line in enumerate(lines):
            if i == is_low_stock_start + 1:
                # Ensure proper indentation (8 spaces for method body)
                fixed_lines.append("        return self.stock <= self.low_stock_threshold\n")
            else:
                fixed_lines.append(line)
        
        # Write the fixed content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        logger.info("Successfully fixed indentation error in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing app.py: {e}")
        return False

if __name__ == "__main__":
    print("Running indentation fix for app.py...")
    
    if fix_app_py():
        print("Successfully fixed indentation error in app.py")
        print("\nYou can now run the application with 'python app.py'")
    else:
        print("Failed to fix indentation error in app.py")
