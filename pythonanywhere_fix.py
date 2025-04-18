"""
Script to fix user authentication issues on PythonAnywhere.
This script should be run on PythonAnywhere to ensure the admin and cashier users exist.
"""
import os
import sys
from werkzeug.security import generate_password_hash
import sqlite3

# Get the path to the database file on PythonAnywhere
# This is typically in the instance directory
DB_PATH = 'instance/inventory.db'  # Adjust this path if needed

def fix_users():
    """Create or update admin and cashier users in the database."""
    print("Starting user fix for PythonAnywhere...")
    
    # Check if database file exists
    global DB_PATH  # Declare global at the beginning of the function
    
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        # Try to find the database file
        possible_paths = [
            'inventory.db',
            'instance/inventory.db',
            '../inventory.db',
            '../instance/inventory.db',
            '/home/renoir01/SmartInventory/instance/inventory.db',
            '/home/renoir01/inventory.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found database at {path}")
                DB_PATH = path
                break
        else:
            print("Could not find the database file. Please specify the correct path.")
            return False
    
    print(f"Using database at: {DB_PATH}")
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if the user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("User table does not exist. Creating it...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            ''')
        
        # Add admin user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', generate_password_hash('admin123'), 'admin')
            )
            print("Created admin user 'admin' with password 'admin123'")
        else:
            print("Admin user 'admin' already exists.")
        
        # Add renoir01 admin user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'renoir01'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('renoir01', generate_password_hash('Renoir@654'), 'admin')
            )
            print("Created admin user 'renoir01' with password 'Renoir@654'")
        else:
            print("Admin user 'renoir01' already exists.")
        
        # Add cashier user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'cashier'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('cashier', generate_password_hash('cashier123'), 'cashier')
            )
            print("Created cashier user 'cashier' with password 'cashier123'")
        else:
            print("Cashier user 'cashier' already exists.")
        
        # Add epi cashier user if it doesn't exist
        cursor.execute("SELECT * FROM user WHERE username = 'epi'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                ('epi', generate_password_hash('Epi@654'), 'cashier')
            )
            print("Created cashier user 'epi' with password 'Epi@654'")
        else:
            print("Cashier user 'epi' already exists.")
        
        # Check if purchase_price column exists in product table
        cursor.execute("PRAGMA table_info(product)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add purchase_price column if it doesn't exist
        if 'purchase_price' not in column_names:
            print("Adding 'purchase_price' column to the product table...")
            cursor.execute("ALTER TABLE product ADD COLUMN purchase_price FLOAT DEFAULT 0")
            print("Added purchase_price column to product table")
        else:
            print("purchase_price column already exists in the product table.")
        
        # Commit the transaction
        conn.commit()
        print("Database fix completed successfully.")
        return True
    
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Database fix failed: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_users()
