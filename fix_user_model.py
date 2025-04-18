"""
Script to fix the User model in app.py on PythonAnywhere.
This script will update the app.py file to add UserMixin to the User class.
"""
import os
import re
import sys
import shutil
import datetime

def fix_user_model():
    """Fix the User model in app.py to inherit from UserMixin."""
    print("Starting User model fix...")
    
    # Backup the original app.py file
    backup_file = f"app.py.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2('app.py', backup_file)
    print(f"Created backup of app.py as {backup_file}")
    
    # Read the app.py file
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if UserMixin is imported
    if 'UserMixin' not in content:
        print("UserMixin not found in imports. Adding it...")
        # Add UserMixin to the import
        content = content.replace(
            "from flask_login import LoginManager, login_user, login_required, logout_user, current_user",
            "from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user"
        )
    else:
        print("UserMixin already in imports.")
    
    # Check if User class inherits from UserMixin
    if 'class User(db.Model, UserMixin):' not in content:
        print("User class does not inherit from UserMixin. Adding it...")
        # Add UserMixin to the User class
        content = content.replace(
            "class User(db.Model):",
            "class User(db.Model, UserMixin):"
        )
    else:
        print("User class already inherits from UserMixin.")
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("User model fix completed. Please reload your web app on PythonAnywhere.")

if __name__ == "__main__":
    fix_user_model()
