"""
Script to initialize the database on PythonAnywhere with standard users and tables.
"""
import os
from app import app, db, User

def initialize_database():
    """Initialize the database with tables and standard users."""
    print("Initializing database...")
    
    # Check database path
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        
        # Create directory if needed
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created directory: {db_dir}")
    
    # Create tables
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully.")
        
        # Add standard users if they don't exist
        print("\nAdding standard users...")
        
        # Admin user
        if not User.query.filter_by(username='renoir01').first():
            admin = User(username='renoir01', role='admin')
            admin.set_password('Renoir@654')
            db.session.add(admin)
            print("Added admin user (username: renoir01, password: Renoir@654)")
        else:
            print("Admin user already exists.")
        
        # Cashier user
        if not User.query.filter_by(username='epi').first():
            cashier = User(username='epi', role='cashier')
            cashier.set_password('Epi@654')
            db.session.add(cashier)
            print("Added cashier user (username: epi, password: Epi@654)")
        else:
            print("Cashier user already exists.")
        
        # Commit changes
        db.session.commit()
        print("Users added successfully.")
        
        # List all users
        users = User.query.all()
        print(f"\nUsers in database ({len(users)}):")
        for user in users:
            print(f"- {user.username} (role: {user.role})")
    
    print("\nDatabase initialization complete.")

if __name__ == "__main__":
    initialize_database()
