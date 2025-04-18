import sqlite3
import os
from datetime import datetime

# Path to the database file
DB_PATH = 'instance/inventory.db'

def migrate_database():
    """Migrate the database to add new fields for packaged products."""
    print("Starting database migration...")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return False
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'is_packaged' not in columns:
            print("Adding 'is_packaged' column to product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN is_packaged BOOLEAN DEFAULT 0")
        
        if 'units_per_package' not in columns:
            print("Adding 'units_per_package' column to product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN units_per_package INTEGER DEFAULT 1")
        
        if 'individual_price' not in columns:
            print("Adding 'individual_price' column to product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN individual_price FLOAT DEFAULT 0")
        
        if 'individual_stock' not in columns:
            print("Adding 'individual_stock' column to product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN individual_stock INTEGER DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        print("Database migration completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
