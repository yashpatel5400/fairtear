"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

import pickle

from compilers.simple import SimpleCompiler
from compilers.recursive import RecursiveCompiler
from classifiers.decisiontree import DTCompiler

def compile(dataset, sensitive_attrs, clf_pickle, features, targets, outfr):
    rc = RecursiveCompiler(incsv=dataset, outfr=outfr, maxdepth=2)
    rc.compile()

    clf = pickle.loads(clf_pickle)
    dtc = DTCompiler(clf=clf, features=features, targets=targets, outfr=outfr)
    dtc.extract()

    rc.frwrite()
    dtc.frwrite()

if __name__ == "__main__":
    dataset         = "tests/simple.csv"
    classifier      = 
    sensitive_attrs = 
    features        = 
    targets         = 
    outfr           = "output/recur_ex.fr"
    compile(dataset, sensitive_attrs, clf_pickle, features, targets, outfr)