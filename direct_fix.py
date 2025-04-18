"""
Direct fix script for the Smart Inventory System on PythonAnywhere.
This script directly modifies the database to ensure proper user setup
and fixes the app.py file to resolve redirect loops.
"""
import os
import sys
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("direct_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def backup_file(filepath):
    """Create a backup of a file with timestamp."""
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.{timestamp}.bak"
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    else:
        logger.error(f"File not found: {filepath}")
        return False

def fix_app_file():
    """Fix the app.py file to resolve redirect loops."""
    app_path = "app.py"
    
    # Backup original file
    if not backup_file(app_path):
        return False
    
    try:
        # Read the original file
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Find and replace the problematic routes
        # 1. Fix the index route
        index_route_old = """@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('cashier_dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        # Break potential redirect loops by going directly to login template
        return render_template('login.html')"""
        
        index_route_new = """@app.route('/')
def index():
    # Simple direct rendering to avoid redirect loops
    return render_template('login.html')"""
        
        content = content.replace(index_route_old, index_route_new)
        
        # 2. Fix the login route
        login_route_old = """@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Don't redirect if already authenticated to avoid loops
        # Instead, check role and render appropriate dashboard
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
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
        return render_template('login.html')"""
        
        login_route_new = """@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, go directly to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('cashier_dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                logger.info(f"User {username} logged in successfully")
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('cashier_dashboard'))
            else:
                flash(_('Invalid username or password'), 'danger')
                logger.warning(f"Failed login attempt for user: {username}")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash(_('An error occurred during login. Please try again.'), 'danger')
    
    # Always render login template for GET requests or failed POST
    return render_template('login.html')"""
        
        content = content.replace(login_route_old, login_route_new)
        
        # Write the fixed content
        with open(f"{app_path}.fixed", 'w') as f:
            f.write(content)
        
        logger.info(f"Created fixed app file: {app_path}.fixed")
        logger.info("To apply the fix, run: cp app.py.fixed app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing app file: {str(e)}")
        return False

def ensure_users_exist():
    """Ensure admin and cashier users exist in the database."""
    try:
        # Import from app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app, db, User
        
        with app.app_context():
            # Check for admin user
            admin = User.query.filter_by(username='renoir01').first()
            if not admin:
                admin = User(username='renoir01', role='admin')
                admin.set_password('Renoir@654')
                db.session.add(admin)
                logger.info("Added admin user: renoir01")
            else:
                logger.info("Admin user already exists: renoir01")
            
            # Check for cashier user
            cashier = User.query.filter_by(username='epi').first()
            if not cashier:
                cashier = User(username='epi', role='cashier')
                cashier.set_password('Epi@654')
                db.session.add(cashier)
                logger.info("Added cashier user: epi")
            else:
                logger.info("Cashier user already exists: epi")
            
            # Commit changes
            db.session.commit()
            
            # List all users
            users = User.query.all()
            logger.info(f"Users in database ({len(users)}):")
            for user in users:
                logger.info(f"- {user.username} (role: {user.role})")
            
            return True
    except Exception as e:
        logger.error(f"Error ensuring users exist: {str(e)}")
        return False

def run_fixes():
    """Run all fixes."""
    logger.info("Starting direct fixes for Smart Inventory System...")
    
    # Fix the app file
    if fix_app_file():
        logger.info("✓ App file fixed successfully")
    else:
        logger.error("✗ Failed to fix app file")
    
    # Ensure users exist
    if ensure_users_exist():
        logger.info("✓ Users verified/created successfully")
    else:
        logger.error("✗ Failed to verify/create users")
    
    logger.info("Direct fixes complete. Check the log for details.")
    logger.info("To apply the app.py fix, run: cp app.py.fixed app.py")
    logger.info("Then reload your web app from the PythonAnywhere dashboard.")

if __name__ == "__main__":
    run_fixes()
