# Smart Inventory and Sales Management System

A lightweight yet powerful web-based application designed to help small businesses monitor product entries, daily sales, and stock levels with precision and ease. Built using Python and Flask, this system provides transparency and accountability in business operations, minimizing losses due to theft or errors.

## Features

 

- **User Authentication**: Secure login system with role-based access control (Admin and Cashier roles)
- **Product Management**: Add, edit, and delete products with details like name, description, price, and stock level
- **Product Categorization**: Organize products into categories (Grains, Vegetables, Fruits, Dairy, etc.)
- **Category-based Sales Reporting**: View and filter sales data by product categories
- **Sales Processing**: Record sales transactions with automatic stock updates
- **Low Stock Alerts**: Get notified when product stock falls below a defined threshold
- **Sales Reports**: View detailed sales history with filtering options
- **Dashboard**: Quick overview of key metrics like revenue, top-selling products, and low stock items

 

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/smart-inventory.git
cd smart-inventory
```

2. Create a virtual environment and activate it:
```
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:
```
SECRET_KEY=your_secret_key_here
```

5. Initialize the database:
```
# Windows
python app.py

# Linux/Mac
python app.py
```

## Usage

1. Run the application:
```
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Login with the default credentials:
   - Admin: username `renoir01`, password `Renoir@654`
   - Cashier: username `cashier`, password `cashier123`

## Default Accounts

The system comes with two default accounts:

- **Admin Account**
  - Username: renoir01
  - Password: Renoir@654
  - Role: Administrator with full access

- **Cashier Account**
  - Username: cashier
  - Password: cashier123
  - Role: Cashier with restricted access

*Note: It is recommended to change these default passwords after the first login for security reasons.*

## Security Considerations

- Change default passwords immediately after installation
- Regularly backup the database file
- Keep the application and its dependencies updated
- Use HTTPS if deploying to a production environment

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- SQLAlchemy ORM
- Bootstrap CSS framework
- Font Awesome icons
