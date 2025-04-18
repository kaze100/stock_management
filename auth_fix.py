#!/usr/bin/env python
"""
Authentication Fix for Smart Inventory System
This script completely rewrites the authentication logic to fix the redirect loop issue
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
        logging.FileHandler("auth_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auth_fix")

def fix_auth_logic():
    """Completely rewrite the authentication logic in app.py"""
    logger.info("Rewriting authentication logic in app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.auth_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Flask app initialization
        app_init_start = content.find("app = Flask(__name__)")
        if app_init_start == -1:
            logger.warning("Could not find Flask app initialization")
            return False
        
        # Find the login manager initialization
        login_manager_start = content.find("# Initialize LoginManager")
        if login_manager_start == -1:
            logger.warning("Could not find login manager initialization")
            return False
        
        login_manager_end = content.find("\n\n", login_manager_start)
        if login_manager_end == -1:
            login_manager_end = content.find("# Helper function", login_manager_start)
            if login_manager_end == -1:
                logger.warning("Could not find end of login manager initialization")
                return False
        
        # Replace the login manager initialization
        new_login_manager = """# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
"""
        
        updated_content = content[:login_manager_start] + new_login_manager + content[login_manager_end:]
        
        # Find the index route
        index_route_start = updated_content.find("@app.route('/')")
        if index_route_start == -1:
            logger.warning("Could not find index route")
            return False
        
        # Find the next route after index
        next_route_start = updated_content.find("@app.route", index_route_start + 1)
        if next_route_start == -1:
            logger.warning("Could not find next route after index")
            return False
        
        # Replace the index route
        new_index_route = """@app.route('/')
def index():
    # Simple index route that just renders the login page
    # No redirects that could cause loops
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'cashier':
            return redirect(url_for('cashier_dashboard'))
    return render_template('login.html')

"""
        
        updated_content = updated_content[:index_route_start] + new_index_route + updated_content[next_route_start:]
        
        # Find the login route
        login_route_start = updated_content.find("@app.route('/login'")
        if login_route_start == -1:
            logger.warning("Could not find login route")
            return False
        
        # Find the next route after login
        next_route_start = updated_content.find("@app.route", login_route_start + 1)
        if next_route_start == -1:
            logger.warning("Could not find next route after login")
            return False
        
        # Replace the login route
        new_login_route = """@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'cashier':
            return redirect(url_for('cashier_dashboard'))
    
    # Handle login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        # Check credentials
        if user and user.check_password(password):
            # Log in the user
            login_user(user)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('cashier_dashboard'))
        else:
            flash(_('Invalid username or password'), 'danger')
    
    # Show login form
    return render_template('login.html')

"""
        
        updated_content = updated_content[:login_route_start] + new_login_route + updated_content[next_route_start:]
        
        # Find the logout route
        logout_route_start = updated_content.find("@app.route('/logout')")
        if logout_route_start == -1:
            logger.warning("Could not find logout route")
            return False
        
        # Find the next route after logout
        next_route_start = updated_content.find("@app.route", logout_route_start + 1)
        if next_route_start == -1:
            logger.warning("Could not find next route after logout")
            return False
        
        # Replace the logout route
        new_logout_route = """@app.route('/logout')
@login_required
def logout():
    # Clear the user session
    logout_user()
    
    # Clear all session data to prevent issues
    session.clear()
    
    # Notify the user
    flash(_('You have been logged out'), 'info')
    
    # Redirect to login page
    return redirect(url_for('login'))

"""
        
        updated_content = updated_content[:logout_route_start] + new_logout_route + updated_content[next_route_start:]
        
        # Find the user_loader function
        user_loader_start = updated_content.find("@login_manager.user_loader")
        if user_loader_start == -1:
            logger.warning("Could not find user_loader function")
            return False
        
        # Find the next function after user_loader
        next_function_start = updated_content.find("@app.route", user_loader_start + 1)
        if next_function_start == -1:
            logger.warning("Could not find next function after user_loader")
            return False
        
        # Replace the user_loader function
        new_user_loader = """@login_manager.user_loader
def load_user(user_id):
    # Simple user loader that returns the user by ID
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

"""
        
        updated_content = updated_content[:user_loader_start] + new_user_loader + updated_content[next_function_start:]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("Successfully rewrote authentication logic in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing authentication logic: {e}")
        return False

if __name__ == "__main__":
    print("Running authentication fix for Smart Inventory System...")
    
    if fix_auth_logic():
        print("Successfully rewrote authentication logic in app.py")
        print("\nAuthentication fix completed!")
        print("\nInstructions:")
        print("1. Stop any running Flask server")
        print("2. Clear your browser cookies and cache completely")
        print("3. Run 'python app.py' to start the server again")
        print("4. Try accessing the site at http://127.0.0.1:5000")
        print("5. If it works, push the changes to GitHub")
        print("6. On PythonAnywhere, pull the changes and reload the web app")
    else:
        print("Failed to rewrite authentication logic in app.py")
