import sys
import os

# Add your project directory to the path
path = '/home/renoir0/SmartInventory'  # Corrected case: capital 'S' in SmartInventory
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'

# Import your app
from app import app as application
