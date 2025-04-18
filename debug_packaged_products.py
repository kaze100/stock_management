#!/usr/bin/env python
"""
Debug script for packaged products feature
This script helps diagnose and fix issues with the packaged products feature
"""
import os
import sys
import logging
import sqlite3
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_packaged_products.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug_packaged_products")

# Path to the database file - adjust as needed for your deployment environment
DB_PATH = 'instance/inventory.db'
PROD_DB_PATH = '/home/renoir0/SmartInventory/instance/inventory.db'

def check_database_schema():
    """Check the database schema for the product table"""
    logger.info("Checking database schema...")
    
    # Determine the correct database path
    db_path = PROD_DB_PATH if os.path.exists(PROD_DB_PATH) else DB_PATH
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(product)")
        columns = cursor.fetchall()
        
        logger.info("Product table schema:")
        for column in columns:
            logger.info(f"Column: {column}")
        
        # Check for specific columns
        column_names = [column[1] for column in columns]
        logger.info(f"Column names: {column_names}")
        
        # Check for NULL values in the new columns
        for column_name in ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']:
            if column_name in column_names:
                cursor.execute(f"SELECT COUNT(*) FROM product WHERE {column_name} IS NULL")
                null_count = cursor.fetchone()[0]
                logger.info(f"Column '{column_name}' has {null_count} NULL values")
        
        # Close the connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False

def fix_database_issues():
    """Fix common database issues with packaged products"""
    logger.info("Fixing database issues...")
    
    # Determine the correct database path
    db_path = PROD_DB_PATH if os.path.exists(PROD_DB_PATH) else DB_PATH
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Set default values for all columns that might be NULL
        cursor.execute("""
            UPDATE product 
            SET 
                is_packaged = COALESCE(is_packaged, 0),
                units_per_package = COALESCE(units_per_package, 1),
                individual_price = COALESCE(individual_price, price),
                individual_stock = COALESCE(individual_stock, 0)
        """)
        
        # Verify no NULL values remain
        for column_name in ['is_packaged', 'units_per_package', 'individual_price', 'individual_stock']:
            cursor.execute(f"SELECT COUNT(*) FROM product WHERE {column_name} IS NULL")
            null_count = cursor.fetchone()[0]
            logger.info(f"After fix: Column '{column_name}' has {null_count} NULL values")
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False

def check_python_error_log():
    """Check the Python error log for relevant errors"""
    logger.info("Checking Python error log...")
    
    error_log_path = "/var/log/renoir0.pythonanywhere.com.error.log"
    if os.path.exists(error_log_path):
        try:
            with open(error_log_path, 'r') as f:
                # Get the last 50 lines of the error log
                lines = f.readlines()[-50:]
                logger.info("Last 50 lines of error log:")
                for line in lines:
                    logger.info(line.strip())
        except Exception as e:
            logger.error(f"Error reading error log: {e}")
    else:
        logger.info(f"Error log not found at {error_log_path}")
        
        # Try to find the error log
        try:
            import glob
            error_logs = glob.glob("/var/log/*.error.log")
            logger.info(f"Found error logs: {error_logs}")
        except Exception as e:
            logger.error(f"Error searching for error logs: {e}")

if __name__ == "__main__":
    print("Running debug for packaged products feature...")
    
    # Check database schema
    check_database_schema()
    
    # Fix database issues
    fix_database_issues()
    
    # Check Python error log
    check_python_error_log()
    
    print("Debug completed. Check the debug_packaged_products.log file for details.")
