"""
Database migration script to add packaged products fields to the Product model
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
        logging.FileHandler("migrations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migrations")

# Path to the database file - adjust as needed for your deployment environment
DB_PATH = 'instance/inventory.db'
PROD_DB_PATH = '/home/renoir0/SmartInventory/instance/inventory.db'

def run_migration():
    """Add packaged products fields to the Product table"""
    logger.info("Running migration to add packaged products fields...")
    
    # Determine the correct database path
    db_path = PROD_DB_PATH if os.path.exists(PROD_DB_PATH) else DB_PATH
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add the new columns if they don't exist
        if 'is_packaged' not in columns:
            logger.info("Adding 'is_packaged' column to Product table")
            cursor.execute("ALTER TABLE product ADD COLUMN is_packaged BOOLEAN DEFAULT 0")
        
        if 'units_per_package' not in columns:
            logger.info("Adding 'units_per_package' column to Product table")
            cursor.execute("ALTER TABLE product ADD COLUMN units_per_package INTEGER DEFAULT 1")
        
        if 'individual_price' not in columns:
            logger.info("Adding 'individual_price' column to Product table")
            cursor.execute("ALTER TABLE product ADD COLUMN individual_price FLOAT DEFAULT 0")
        
        if 'individual_stock' not in columns:
            logger.info("Adding 'individual_stock' column to Product table")
            cursor.execute("ALTER TABLE product ADD COLUMN individual_stock INTEGER DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        logger.info("Migration completed successfully")
        
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
    success = run_migration()
    if success:
        print("Migration completed successfully")
        sys.exit(0)
    else:
        print("Migration failed. Check the logs for details.")
        sys.exit(1)
