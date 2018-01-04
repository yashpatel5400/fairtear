"""
__author__ = Yash Patel and Zachary Liu
__name__   = run.py
__description__ = Main file to run to start Flask server
"""

from app import app
app.run(host='0.0.0.0', port=8080, debug=True)