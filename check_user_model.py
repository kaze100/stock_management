"""
Script to check and fix the User model in the database to ensure it's compatible with Flask-Login.
"""
import os
import sys
import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Import the app and User model
try:
    from app import app, User, db
    print("Successfully imported app and User model")
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def check_user_model():
    """Check if the User model has the required Flask-Login attributes."""
    print("\nChecking User model...")
    
    # Check if User inherits from UserMixin
    if not issubclass(User, UserMixin):
        print("WARNING: User class does not inherit from UserMixin")
        print("This might cause authentication issues with Flask-Login")
    else:
        print("User class correctly inherits from UserMixin")
    
    # Check for required Flask-Login attributes
    required_attrs = ['is_authenticated', 'is_active', 'is_anonymous', 'get_id']
    missing_attrs = []
    
    for attr in required_attrs:
        if not hasattr(User, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        print(f"WARNING: User class is missing these required Flask-Login attributes: {', '.join(missing_attrs)}")
    else:
        print("User class has all required Flask-Login attributes")
    
    # Check if we can instantiate a User object
    try:
        user = User(username="test_user", role="admin")
        user.set_password("password123")
        print("Successfully created a User instance")
        
        # Test the authentication methods
        print(f"is_authenticated: {user.is_authenticated}")
        print(f"is_active: {user.is_active}")
        print(f"is_anonymous: {user.is_anonymous}")
        print(f"get_id(): {user.get_id()}")
        
    except Exception as e:
        print(f"Error creating User instance: {e}")
    
    # Check the database for existing users
    with app.app_context():
        try:
            users = User.query.all()
            print(f"\nFound {len(users)} users in the database:")
            for user in users:
                print(f"- {user.username} (role: {user.role})")
        except Exception as e:
            print(f"Error querying users: {e}")

if __name__ == "__main__":
    check_user_model()
