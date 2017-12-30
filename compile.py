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
    """Main function, used to compile into the final .fr file. Takes the dataset and
    sensitive_attrs to construct the popModel() function and clf, features, and target
    for F(). Outputs are saved to the outfr destination (returns void)

    Parameters
    ----------
    dataset : str
        Filename of the csv where the input dataset is stored

    sensitive_attrs : list of str
        List of the names of attributes to be considered sensitive. Must match a column
        from the input dataset

    clf_pickle : str
        Filename of where a pickled classifier is saved

    features : list of str
        List of input features used to train clf. Must match columns from the input dataset

    targets : str
        Name of the clf target variable. Must match a column from the input dataset

    outfr : str
        Filename where the output (.fr file) is to be stored
    """
    rc = RecursiveCompiler(incsv=dataset, outfr=outfr, maxdepth=2)
    rc.compile()

    clf = pickle.loads(clf_pickle)
    dtc = DTCompiler(clf=clf, features=features, targets=targets, outfr=outfr)
    dtc.extract()

    rc.frwrite()
    dtc.frwrite()

if __name__ == "__main__":
    dataset         = "tests/simple.csv"
    classifier      = "classifiers/examples/decisiontree.pickle"
    sensitive_attrs = ["ethnicity"]
    features        = ["ethnicity", "colRank", "yExp"]
    targets         = ["hire"]
    outfr           = "output/recur_ex.fr"
    compile(dataset, sensitive_attrs, clf_pickle, features, targets, outfr)