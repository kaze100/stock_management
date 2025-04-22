from app import app, db
from sqlalchemy import Column, Boolean, Integer, Float

# Run this script to add missing columns to the Product table
with app.app_context():
    # Check if columns exist and add them if they don't
    with db.engine.connect() as conn:
        # Check if is_packaged column exists
        result = conn.execute("PRAGMA table_info(product)")
        columns = [row[1] for row in result.fetchall()]
        
        # Add missing columns if they don't exist
        if 'is_packaged' not in columns:
            conn.execute("ALTER TABLE product ADD COLUMN is_packaged BOOLEAN DEFAULT 0")
            print("Added is_packaged column")
        
        if 'units_per_package' not in columns:
            conn.execute("ALTER TABLE product ADD COLUMN units_per_package INTEGER DEFAULT 1")
            print("Added units_per_package column")
        
        if 'individual_price' not in columns:
            conn.execute("ALTER TABLE product ADD COLUMN individual_price FLOAT DEFAULT 0")
            print("Added individual_price column")
        
        if 'individual_stock' not in columns:
            conn.execute("ALTER TABLE product ADD COLUMN individual_stock INTEGER DEFAULT 0")
            print("Added individual_stock column")
        
    print("Database schema update complete!")
