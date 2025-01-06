import os
import sys
import webbrowser
from threading import Timer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    from app import app
    
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        app.template_folder = template_folder
    
    # Don't open browser in development
    if os.environ.get('FLASK_ENV') != 'development':
        Timer(1.5, open_browser).start()
    
    app.run(port=5000)
