from app import app, db, User, Product
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database with tables and default admin user."""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Creating default admin user...")
            admin = User(
                username='renoir01',
                password_hash=generate_password_hash('Renoir@654'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created.")
        else:
            print("Admin user already exists.")
        
        print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
