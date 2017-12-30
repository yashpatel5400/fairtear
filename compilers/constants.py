"""
__author__ = Yash Patel and Zachary Liu
__name__   = constants.py
__description__ = Compiler-level constants
"""

# empirically determined value of where to stop recursion/splitting of the tree
INFORMATION_GAIN_THRESH = 0.0

# the partition must contain at least 10% of the data to be considered valid
PARTITION_FRAC_THRESH = 0.10

# hard cutoff on the maximum number of levels of conditionals (i.e. in the tree)
RECURSION_CUTOFF = 2