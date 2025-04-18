"""
Script to check database configuration and users on PythonAnywhere.
"""
from app import app, User, db

def check_db_config():
    """Check database configuration and users."""
    print("Checking database configuration...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("\nChecking users in the database...")
    with app.app_context():
        users = User.query.all()
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"- {user.username} (role: {user.role})")
        else:
            print("No users found in the database.")
    
    print("\nCreating a test admin user...")
    with app.app_context():
        if not User.query.filter_by(username='testadmin').first():
            user = User(username='testadmin', role='admin')
            user.set_password('Test@123')
            db.session.add(user)
            db.session.commit()
            print("Created test admin user 'testadmin' with password 'Test@123'")
        else:
            print("Test admin user 'testadmin' already exists.")

if __name__ == "__main__":
    check_db_config()
