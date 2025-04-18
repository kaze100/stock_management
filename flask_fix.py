#!/usr/bin/env python
"""
Flask Fix for Smart Inventory System
This script fixes the @app.before_first_request issue in Flask 2.0+
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
        logging.FileHandler("flask_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("flask_fix")

def fix_app_py():
    """Fix the @app.before_first_request issue in Flask 2.0+"""
    logger.info("Fixing Flask 2.0+ compatibility issue in app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.flask_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace @app.before_first_request with a different approach
        if '@app.before_first_request' in content:
            # Find the function definition
            start_idx = content.find('@app.before_first_request')
            end_idx = content.find('if __name__ ==', start_idx)
            
            if start_idx != -1 and end_idx != -1:
                # Extract the function body
                function_code = content[start_idx:end_idx].strip()
                
                # Create a new function to initialize the database
                new_function_code = """
# Initialize the database
def initialize_database():
    try:
        logger.info("Initializing database")
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='renoir01').first()
        if not admin:
            admin = User(username='renoir01', role='admin')
            admin.set_password('Renoir@654')
            db.session.add(admin)
            logger.info("Admin user created")
        
        # Check if cashier user exists
        cashier = User.query.filter_by(username='epi').first()
        if not cashier:
            cashier = User(username='epi', role='cashier')
            cashier.set_password('Epi@654')
            db.session.add(cashier)
            logger.info("Cashier user created")
        
        db.session.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_database()
    app.run(debug=True)
"""
                
                # Replace the old code with the new code
                updated_content = content[:start_idx] + new_function_code
                
                # Write the updated content back to app.py
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info("Successfully fixed Flask 2.0+ compatibility issue in app.py")
                return True
            else:
                logger.warning("Could not find the end of the before_first_request function")
                return False
        else:
            logger.info("No @app.before_first_request found in app.py")
            return True
    
    except Exception as e:
        logger.error(f"Error fixing app.py: {e}")
        return False

if __name__ == "__main__":
    print("Running Flask 2.0+ compatibility fix for Smart Inventory System...")
    
    if fix_app_py():
        print("Successfully fixed Flask 2.0+ compatibility issue in app.py")
        print("\nFlask fix completed!")
        print("\nInstructions:")
        print("1. Run 'python app.py' to test locally")
        print("2. If it works, push the changes to GitHub")
        print("3. On PythonAnywhere, pull the changes and reload the web app")
        print("4. Clear your browser cookies and cache")
        print("5. Try accessing the site again")
    else:
        print("Failed to fix Flask 2.0+ compatibility issue in app.py")
