"""
Comprehensive database initialization script for Smart Inventory System.
This script will:
1. Create all necessary tables
2. Add admin and cashier users
3. Ensure the purchase_price column exists
"""
import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime
import sqlite3

# Path to the database file
DB_PATH = 'new_inventory.db'

def initialize_database():
    """Initialize the database with all required tables and users."""
    print("Starting comprehensive database initialization...")
    
    # Remove existing file if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database file: {DB_PATH}")
    
    # Connect to the database (this will create a new file)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create user table
        print("Creating user table...")
        cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # Create product table with purchase_price column
        print("Creating product table...")
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
        print("Creating sale table...")
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
        
        # Add admin users
        print("Adding admin users...")
        admin_users = [
            ('admin', generate_password_hash('admin123'), 'admin'),
            ('renoir01', generate_password_hash('Renoir@654'), 'admin')
        ]
        
        for username, password_hash, role in admin_users:
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            print(f"Added admin user: {username}")
        
        # Add cashier users
        print("Adding cashier users...")
        cashier_users = [
            ('cashier', generate_password_hash('cashier123'), 'cashier'),
            ('epi', generate_password_hash('Epi@654'), 'cashier')
        ]
        
        for username, password_hash, role in cashier_users:
            cursor.execute(
                "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            print(f"Added cashier user: {username}")
        
        # Commit the transaction
        conn.commit()
        print("Database initialization completed successfully.")
        return True
    
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Database initialization failed: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
