"""
Debug script to fix login issues on PythonAnywhere.
This script creates a direct login page that bypasses the problematic routes.
"""
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, current_user
from werkzeug.security import check_password_hash
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_login.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_debug_app():
    """Create a minimal Flask app for debugging login."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'debug-secret-key'
    
    # Initialize LoginManager
    login_manager = LoginManager(app)
    
    try:
        # Import the User model and db from the main app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import User, db, app as main_app
        
        # Use the same database configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = main_app.config['SQLALCHEMY_DATABASE_URI']
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        @app.route('/')
        def index():
            return render_template('debug_login.html')
        
        @app.route('/debug_login', methods=['POST'])
        def debug_login():
            username = request.form.get('username')
            password = request.form.get('password')
            
            logger.info(f"Attempting login for user: {username}")
            
            with main_app.app_context():
                user = User.query.filter_by(username=username).first()
                
                if user:
                    logger.info(f"User found: {user.username}, role: {user.role}")
                    if check_password_hash(user.password_hash, password):
                        login_user(user)
                        logger.info(f"Login successful for {user.username}")
                        
                        # Direct links to dashboards
                        if user.role == 'admin':
                            return f"""
                            <h1>Login Successful!</h1>
                            <p>You are logged in as: {user.username} (Admin)</p>
                            <p>Use these direct links to access your dashboard:</p>
                            <ul>
                                <li><a href="/admin/dashboard">Admin Dashboard</a></li>
                                <li><a href="/admin/products">Manage Products</a></li>
                                <li><a href="/admin/sales">View Sales</a></li>
                            </ul>
                            """
                        else:
                            return f"""
                            <h1>Login Successful!</h1>
                            <p>You are logged in as: {user.username} (Cashier)</p>
                            <p>Use these direct links to access your dashboard:</p>
                            <ul>
                                <li><a href="/cashier/dashboard">Cashier Dashboard</a></li>
                                <li><a href="/cashier/sales">View Sales</a></li>
                            </ul>
                            """
                    else:
                        logger.warning(f"Invalid password for user: {username}")
                        return "<h1>Login Failed</h1><p>Invalid password. <a href='/'>Try again</a></p>"
                else:
                    logger.warning(f"User not found: {username}")
                    return "<h1>Login Failed</h1><p>User not found. <a href='/'>Try again</a></p>"
        
        return app
    
    except Exception as e:
        logger.error(f"Error creating debug app: {str(e)}")
        
        @app.route('/')
        def error_index():
            return f"<h1>Error</h1><p>Could not initialize debug app: {str(e)}</p>"
        
        return app

if __name__ == "__main__":
    app = create_debug_app()
    app.run(debug=True, port=8080)
