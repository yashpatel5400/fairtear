"""
__author__ = Yash Patel and Zachary Liu
__name__   = constants.py
__description__ = Compiler-level constants
"""

# empirically determined value of where to stop recursion/splitting of the tree
INFORMATION_GAIN_THRESH = 0.125

# hard cutoff on the maximum number of levels of conditionals (i.e. in the tree)
RECURSION_CUTOFF = 2