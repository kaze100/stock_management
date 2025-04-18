#!/usr/bin/env python
"""
Redirect Loop Fix for Smart Inventory System
This script fixes the redirect loop issue in the application
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
        logging.FileHandler("redirect_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("redirect_fix")

def fix_redirect_loop():
    """Fix the redirect loop issue in app.py"""
    logger.info("Fixing redirect loop issue in app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.redirect_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the index route to prevent redirect loops
        index_route = """@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'cashier':
                return redirect(url_for('cashier_dashboard'))
        # If not authenticated, render login page directly instead of redirecting
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash(_('An error occurred. Please try again.'), 'danger')
        return render_template('login.html')
"""
        
        # Find the index route in the content
        start_idx = content.find("@app.route('/')")
        if start_idx == -1:
            logger.warning("Could not find index route")
            return False
        
        # Find the end of the index route
        end_idx = content.find("@app.route", start_idx + 1)
        if end_idx == -1:
            logger.warning("Could not find end of index route")
            return False
        
        # Replace the index route
        updated_content = content[:start_idx] + index_route + content[end_idx:]
        
        # Fix the login route to prevent redirect loops
        login_route = """@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # If user is already authenticated, redirect to appropriate dashboard
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'cashier':
                return redirect(url_for('cashier_dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('cashier_dashboard'))
            else:
                flash(_('Invalid username or password'), 'danger')
        
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        flash(_('An error occurred. Please try again.'), 'danger')
        return render_template('login.html')
"""
        
        # Find the login route in the updated content
        start_idx = updated_content.find("@app.route('/login'")
        if start_idx == -1:
            logger.warning("Could not find login route")
            return False
        
        # Find the end of the login route
        end_idx = updated_content.find("@app.route", start_idx + 1)
        if end_idx == -1:
            logger.warning("Could not find end of login route")
            return False
        
        # Replace the login route
        updated_content = updated_content[:start_idx] + login_route + updated_content[end_idx:]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("Successfully fixed redirect loop issue in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing redirect loop: {e}")
        return False

if __name__ == "__main__":
    print("Running redirect loop fix for Smart Inventory System...")
    
    if fix_redirect_loop():
        print("Successfully fixed redirect loop issue in app.py")
        print("\nRedirect fix completed!")
        print("\nInstructions:")
        print("1. Run 'python app.py' to test locally")
        print("2. Clear your browser cookies and cache")
        print("3. Try accessing the site again")
        print("4. If it works, push the changes to GitHub")
        print("5. On PythonAnywhere, pull the changes and reload the web app")
    else:
        print("Failed to fix redirect loop issue in app.py")
