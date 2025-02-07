import PyInstaller.__main__
import os

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

PyInstaller.__main__.run([
    'desktop_app.py',
    '--onefile',
    '--windowed',
    '--icon=static/favicon.ico' if os.path.exists('static/favicon.ico') else None,
    '--name=Employify',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--hidden-import=flask',
    '--hidden-import=flask_sqlalchemy',
    '--hidden-import=flask_login',
])
