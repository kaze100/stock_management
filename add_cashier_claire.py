import os
from app import db, User
from werkzeug.security import generate_password_hash

def add_cashier():
    username = 'claire'
    password = 'Claire@654'
    role = 'cashier'

    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
        return

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()
    print(f"Cashier '{username}' created successfully.")

if __name__ == '__main__':
    add_cashier()
