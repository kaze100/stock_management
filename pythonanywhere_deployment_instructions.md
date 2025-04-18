# Smart Inventory System - PythonAnywhere Deployment Instructions

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
