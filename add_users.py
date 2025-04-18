from app import db, User
from werkzeug.security import generate_password_hash

def add_users():
    """Add additional admin and cashier users to the database."""
    print("Adding additional users...")
    
    # Check if renoir01 admin user already exists
    admin = User.query.filter_by(username='renoir01').first()
    if not admin:
        admin = User(username='renoir01', role='admin')
        admin.set_password('Renoir@654')
        db.session.add(admin)
        print("Created admin user 'renoir01' with password 'Renoir@654'")
    else:
        print("Admin user 'renoir01' already exists.")
    
    # Check if epi cashier user already exists
    cashier = User.query.filter_by(username='epi').first()
    if not cashier:
        cashier = User(username='epi', role='cashier')
        cashier.set_password('Epi@654')
        db.session.add(cashier)
        print("Created cashier user 'epi' with password 'Epi@654'")
    else:
        print("Cashier user 'epi' already exists.")
    
    db.session.commit()
    print("Additional users added successfully.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        add_users()
