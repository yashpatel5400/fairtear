"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Initializes the Flask app server
"""
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')