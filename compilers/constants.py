"""
__author__ = Yash Patel and Zachary Liu
__name__   = constants.py
__description__ = Compiler-level constants
"""

# empirically determined value of where to stop recursion/splitting of the tree
INFORMATION_GAIN_THRESH = 0.10

# the partition must contain at least 10% of the data to be considered valid
PARTITION_FRAC_THRESH = 0.10

# penalty for having too many partitions (avoids overfitting)
PARTITION_PENALTY = .33