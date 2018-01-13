"""
__author__ = Yash Patel and Zachary Liu
__name__   = run.py
__description__ = Main file to run to start Flask server
"""

# ratchet way of getting around namespace issues with FairSquare
import sys
sys.path += ['fairtear/external/fairsquare/src']

from fairtear.app import app

if __name__ == "__main__":
    app.run(port=8080, debug=True, use_debugger=False, use_reloader=False)