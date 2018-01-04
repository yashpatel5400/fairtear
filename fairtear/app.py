"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Main Flask application server
"""

from flask import render_template
from flask_login import login_required, current_user

@app.route('/')
def index():
    return render_template("index.html")