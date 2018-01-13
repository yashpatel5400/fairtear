"""
__author__ = Yash Patel and Zachary Liu
__name__   = config.py
__description__ = Flask application server configuration (options)
"""

import os

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Statement for enabling the development environment
DEBUG = True

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = False
WTF_CSRF_ENABLED = False

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# uploads for the data csvs
UPLOAD_FOLDER = os.path.abspath("fairtear/data")

# only reads csv files for now
ALLOWED_EXTENSIONS = set(['csv','pickle'])