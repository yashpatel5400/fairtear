"""
__author__ = Yash Patel and Zachary Liu
__name__   = __init__.py
__description__ = Initializes the compilers directory of FairTear. Compilers are
the main component of the backend, used to convert from input .csv datasets to
the desired .fr outputs to feed into FairSquare. All .fr files abide by the API:

__init__(self, csv, outfr, [params]): Initializes a compiler to take data from the 
    file pointed at by the csv string and output its results to the corresponding 
    outfr location. Params are required for some of the more complicated compilers

compile(): Compiles the input csv file into an internal program-tree structure

frwrite(): Takes the program tree and produces a corresponding .fr file
"""