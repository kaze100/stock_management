"""
Smart Inventory System - PythonAnywhere Deployment Script
--------------------------------------------------------
This script helps prepare your application for deployment to PythonAnywhere.
It creates the necessary files and provides instructions for deployment.
"""

import os
import sys
import shutil

def create_wsgi_file():
    """Create the WSGI file needed by PythonAnywhere"""
    wsgi_content = """import sys
import os

# Add your project directory to the sys.path
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/smart_inventory'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables (if needed)
os.environ['FLASK_ENV'] = 'production'

# Import your Flask app
from app import app as application
"""
    
    with open('pythonanywhere_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    print("✅ Created WSGI file: pythonanywhere_wsgi.py")

def create_requirements_file():
    """Create requirements.txt file for PythonAnywhere"""
    requirements = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-Login==0.6.3",
        "Flask-Babel==4.0.0",
        "Werkzeug==2.3.7",
        "SQLAlchemy==2.0.23",
        "Babel==2.13.1",
        "Jinja2==3.1.2",
        "itsdangerous==2.1.2",
        "click==8.1.7",
        "MarkupSafe==2.1.3",
        "pytz==2023.3.post1",
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    print("✅ Created requirements.txt file")

def create_deployment_instructions():
    """Create a file with deployment instructions"""
    instructions = """# Smart Inventory System - PythonAnywhere Deployment Instructions

## 1. Create a PythonAnywhere Account
If you don't already have one, create a free account at https://www.pythonanywhere.com/

## 2. Upload Your Files
- Log in to PythonAnywhere
- Go to the "Files" tab
- Create a new directory called "smart_inventory"
- Upload all your project files to this directory

## 3. Set Up a Virtual Environment
- Go to the "Consoles" tab
- Start a new Bash console
- Run the following commands:

```bash
cd ~/smart_inventory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configure the Web App
- Go to the "Web" tab
- Click "Add a new web app"
- Choose "Manual configuration" (not Flask)
- Select Python 3.10 (or the version closest to your local environment)
- Set the following configuration:
  - Source code: /home/YOUR_USERNAME/smart_inventory
  - Working directory: /home/YOUR_USERNAME/smart_inventory
  - WSGI configuration file: Edit this file and replace the content with what's in your pythonanywhere_wsgi.py
  - Virtual environment: /home/YOUR_USERNAME/smart_inventory/venv

## 5. Initialize the Database
- Go back to the "Consoles" tab
- In your Bash console, run:

```bash
cd ~/smart_inventory
source venv/bin/activate
python
```

- In the Python console, run:

```python
from app import db, initialize_database
db.create_all()
initialize_database()
exit()
```

## 6. Reload the Web App
- Go back to the "Web" tab
- Click the "Reload" button for your web app

## 7. Your app should now be live at:
https://YOUR_USERNAME.pythonanywhere.com/

## Troubleshooting
- Check the error logs in the "Web" tab if you encounter any issues
- Make sure all paths in the WSGI file match your actual directory structure
- Ensure all required packages are in requirements.txt
"""
    
    with open('pythonanywhere_deployment_instructions.md', 'w') as f:
        f.write(instructions)
    print("✅ Created deployment instructions: pythonanywhere_deployment_instructions.md")

def main():
    print("Smart Inventory System - PythonAnywhere Deployment Preparation")
    print("------------------------------------------------------------")
    
    create_wsgi_file()
    create_requirements_file()
    create_deployment_instructions()
    
    print("\n✅ Deployment preparation complete!")
    print("Please follow the instructions in pythonanywhere_deployment_instructions.md to deploy your application.")

if __name__ == "__main__":
    main()
