#!/usr/bin/env python
"""
Fix script for packaged products database migration
This script updates existing products with default values for the new packaged products fields
"""
import sqlite3
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_packaged_products.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_packaged_products")

# Path to the database file - adjust as needed for your deployment environment
DB_PATH = 'instance/inventory.db'
PROD_DB_PATH = '/home/renoir0/SmartInventory/instance/inventory.db'

def fix_database():
    """Update existing products with default values for new packaged products fields"""
    logger.info("Running fix for packaged products database migration...")
    
    # Determine the correct database path
    db_path = PROD_DB_PATH if os.path.exists(PROD_DB_PATH) else DB_PATH
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns exist
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ensure all required columns exist
        required_columns = ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logger.error(f"Missing columns in product table: {missing_columns}")
            logger.info("Adding missing columns...")
            
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
        
        # Update all existing products with default values for the new fields
        logger.info("Updating existing products with default values...")
        cursor.execute("""
            UPDATE product 
            SET 
                is_packaged = 0,
                units_per_package = 1,
                individual_price = price,
                individual_stock = 0
            WHERE 
                is_packaged IS NULL OR
                units_per_package IS NULL OR
                individual_price IS NULL OR
                individual_stock IS NULL
        """)
        
        # Commit the changes
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM product WHERE is_packaged IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            logger.warning(f"There are still {null_count} products with NULL values")
        else:
            logger.info("All products have been updated successfully")
        
        # Close the connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("Database fix completed successfully")
        sys.exit(0)
    else:
        print("Database fix failed. Check the logs for details.")
        sys.exit(1)
