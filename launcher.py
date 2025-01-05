import os
import sys
import webbrowser
from threading import Timer
from app import app

def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        app.template_folder = template_folder
        
    Timer(1.5, open_browser).start()  # Wait for 1.5 seconds before opening browser
    app.run(port=5000)
