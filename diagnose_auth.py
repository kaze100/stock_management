"""
Diagnostic script to verify Flask-Login and User model configuration on PythonAnywhere.
This script will check for common authentication issues without making any changes.
"""
import os
import sys
import inspect
import importlib.util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auth_diagnosis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_app_imports():
    """Check if the app imports Flask-Login correctly."""
    logger.info("Checking app imports...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for UserMixin in imports
        if 'UserMixin' in content:
            logger.info("✓ UserMixin is imported in app.py")
        else:
            logger.error("✗ UserMixin is NOT imported in app.py")
            logger.info("  Expected import: from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user")
        
        # Check User model definition
        if 'class User(db.Model, UserMixin):' in content:
            logger.info("✓ User model inherits from UserMixin")
        else:
            logger.error("✗ User model does NOT inherit from UserMixin")
            logger.info("  Expected definition: class User(db.Model, UserMixin):")
        
        return True
    except Exception as e:
        logger.error(f"Error checking app imports: {str(e)}")
        return False

def check_flask_login_installation():
    """Check if Flask-Login is installed correctly."""
    logger.info("Checking Flask-Login installation...")
    
    try:
        import flask_login
        logger.info(f"✓ Flask-Login is installed (version: {flask_login.__version__})")
        
        # Check for UserMixin
        if hasattr(flask_login, 'UserMixin'):
            logger.info("✓ UserMixin is available in flask_login")
        else:
            logger.error("✗ UserMixin is NOT available in flask_login")
        
        return True
    except ImportError:
        logger.error("✗ Flask-Login is NOT installed")
        return False
    except Exception as e:
        logger.error(f"Error checking Flask-Login: {str(e)}")
        return False

def check_user_model():
    """Check if the User model has the required Flask-Login attributes."""
    logger.info("Checking User model...")
    
    try:
        # Try to import the User model from app
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Check if User is defined
        if hasattr(app_module, 'User'):
            User = app_module.User
            logger.info("✓ User model is defined in app.py")
            
            # Check if User inherits from UserMixin
            from flask_login import UserMixin
            if issubclass(User, UserMixin):
                logger.info("✓ User class correctly inherits from UserMixin")
            else:
                logger.error("✗ User class does NOT inherit from UserMixin")
            
            # Check for required Flask-Login attributes
            required_attrs = ['is_authenticated', 'is_active', 'is_anonymous', 'get_id']
            missing_attrs = []
            
            for attr in required_attrs:
                if not hasattr(User, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                logger.error(f"✗ User class is missing these required Flask-Login attributes: {', '.join(missing_attrs)}")
            else:
                logger.info("✓ User class has all required Flask-Login attributes")
            
            # Check if we can instantiate a User object
            try:
                user = User(username="test_user", role="admin")
                logger.info("✓ Successfully created a User instance")
                
                # Test the authentication methods
                logger.info(f"  is_authenticated: {user.is_authenticated}")
                logger.info(f"  is_active: {user.is_active}")
                logger.info(f"  is_anonymous: {user.is_anonymous}")
                logger.info(f"  get_id(): {user.get_id()}")
                
            except Exception as e:
                logger.error(f"✗ Error creating User instance: {str(e)}")
        else:
            logger.error("✗ User model is NOT defined in app.py")
        
        return True
    except Exception as e:
        logger.error(f"Error checking User model: {str(e)}")
        return False

def check_login_manager():
    """Check if LoginManager is configured correctly."""
    logger.info("Checking LoginManager configuration...")
    
    try:
        # Try to import the app and LoginManager
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Check if LoginManager is initialized
        if hasattr(app_module, 'login_manager'):
            login_manager = app_module.login_manager
            logger.info("✓ LoginManager is initialized")
            
            # Check if user_loader is defined
            if hasattr(app_module, 'load_user'):
                logger.info("✓ user_loader function is defined")
            else:
                logger.error("✗ user_loader function is NOT defined")
            
            return True
        else:
            logger.error("✗ LoginManager is NOT initialized")
            return False
    except Exception as e:
        logger.error(f"Error checking LoginManager: {str(e)}")
        return False

def check_database():
    """Check if the database exists and has users."""
    logger.info("Checking database...")
    
    try:
        # Try to import the app and db
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Check if db is initialized
        if hasattr(app_module, 'db'):
            db = app_module.db
            app = app_module.app
            logger.info("✓ SQLAlchemy db is initialized")
            
            # Check if the database file exists
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            logger.info(f"  Database URI: {db_uri}")
            
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    logger.info(f"✓ Database file exists at {db_path}")
                else:
                    logger.error(f"✗ Database file does NOT exist at {db_path}")
            
            # Check for users in the database
            with app.app_context():
                try:
                    User = app_module.User
                    users = User.query.all()
                    logger.info(f"✓ Found {len(users)} users in the database:")
                    for user in users:
                        logger.info(f"  - {user.username} (role: {user.role})")
                except Exception as e:
                    logger.error(f"✗ Error querying users: {str(e)}")
            
            return True
        else:
            logger.error("✗ SQLAlchemy db is NOT initialized")
            return False
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False

def run_diagnostics():
    """Run all diagnostic checks."""
    logger.info("Starting authentication diagnostics...")
    
    checks = [
        check_app_imports,
        check_flask_login_installation,
        check_user_model,
        check_login_manager,
        check_database
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    if all(results):
        logger.info("All checks completed. See above for any issues.")
    else:
        logger.error("Some checks failed. See above for details.")
    
    logger.info("Authentication diagnostics complete.")
    logger.info("Results saved to auth_diagnosis.log")

if __name__ == "__main__":
    run_diagnostics()
