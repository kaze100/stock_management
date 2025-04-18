import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Path to the database file
DB_PATH = 'instance/inventory.db'

def reset_database():
    """Reset the database by removing all trial data but keeping the admin account."""
    print("Starting database reset...")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return False
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Save admin user info before deleting
        cursor.execute("SELECT id, username, password_hash FROM user WHERE role = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        
        # Delete all data from tables
        cursor.execute("DELETE FROM sale")
        cursor.execute("DELETE FROM product")
        cursor.execute("DELETE FROM user")
        
        # Restore admin user if it existed
        if admin:
            admin_id, admin_username, admin_password_hash = admin
            cursor.execute(
                "INSERT INTO user (id, username, password_hash, role) VALUES (?, ?, ?, ?)",
                (admin_id, admin_username, admin_password_hash, 'admin')
            )
            print(f"Admin user '{admin_username}' has been preserved.")
        else:
            # Create a default admin if none existed
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('renoir01', generate_password_hash('Renoir@654'), 'admin')
            )
            print("Created default admin user 'renoir01' with password 'Renoir@654'")
        
        # Check if purchase_price column exists in product table
        cursor.execute("PRAGMA table_info(product)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add purchase_price column if it doesn't exist
        if 'purchase_price' not in column_names:
            print("Adding 'purchase_price' column to the product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN purchase_price FLOAT DEFAULT 0")
            print("Added purchase_price column to product table")
        
        # Commit the transaction
        conn.commit()
        print("Database reset successful. All trial data has been removed.")
        return True
    
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Database reset failed: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database()
