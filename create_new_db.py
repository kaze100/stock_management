import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Path to the new database file
DB_PATH = 'new_inventory.db'

def create_new_database():
    """Create a completely new database with all required tables and the purchase_price column."""
    print("Creating new database...")
    
    # Remove existing file if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database file: {DB_PATH}")
    
    # Connect to the database (this will create a new file)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create user table
        cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # Create product table with purchase_price column
        cursor.execute('''
        CREATE TABLE product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'Uncategorized',
            purchase_price FLOAT DEFAULT 0,
            price FLOAT NOT NULL,
            stock INTEGER DEFAULT 0,
            low_stock_threshold INTEGER DEFAULT 10,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sale table
        cursor.execute('''
        CREATE TABLE sale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price FLOAT NOT NULL,
            cashier_id INTEGER NOT NULL,
            date_sold TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES product (id),
            FOREIGN KEY (cashier_id) REFERENCES user (id)
        )
        ''')
        
        # Create admin user
        cursor.execute(
            "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin')
        )
        
        # Create cashier user
        cursor.execute(
            "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
            ('cashier', generate_password_hash('cashier123'), 'cashier')
        )
        
        # Commit the transaction
        conn.commit()
        print("New database created successfully with all required tables.")
        print("Created admin user 'admin' with password 'admin123'")
        print("Created cashier user 'cashier' with password 'cashier123'")
        
        return True
    
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Database creation failed: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_new_database()
