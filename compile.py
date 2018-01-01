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

def compile(dataset, clf_pickle, features, target, outfr, 
    sensitive_attrs, qualified_attrs, fairness_targets):
    """Main function, used to compile into the final .fr file. Takes the dataset and
    sensitive_attrs to construct the popModel() function and clf, features, and target
    for F(). Outputs are saved to the outfr destination (returns void)

    Parameters
    ----------
    dataset : str
        Filename of the csv where the input dataset is stored

    clf_pickle : str
        Filename of where a pickled classifier is saved

    features : list of str
        List of input features used to train clf. Must match columns from the input dataset

    target : str
        Name of the clf target variable. Must match a column from the input dataset

    outfr : str
        Filename where the output (.fr file) is to be stored

    sensitive_attrs : list of (str,str,int) tuples
        List of the names of attributes to be considered sensitive. Each attr has a
        "threshold" value, where we wish to mask whether the an individual's sensitive 
        attribute in relation to that threshold based on the 2nd param of the tuple. 
        The second param MUST either be ">" or "<", which respectively mean to hide 
        being below or exceeding a given threshold value. For example, if 
        the attribute is sex (step([0,1,.5],[1,2,.5])), the threshold can be set to 1
        w/ "<" to prevent us from knowing if (sex < 1)

    qualified_attrs : list of (str,str,int) tuples
        Same structure as sensitive_attrs. Used to qualify only particular members of the
        population, i.e. those satisfying the qualified conditionals. For example, if doing
        ("age",">",18), only those people of > 18 age will be considered in the population

    fairness_targets : list of (str,str,int) tuples
        Same structure as sensitive_attrs. Denotes the desired fairness criterion, i.e.
        ("hire",">",0.5) corresponds to wanting to ensure the population satisfies hire > 0.5
        independent of sensitive attributes
    """
    rc = RecursiveCompiler(incsv=dataset, outfr=outfr, maxdepth=2, features=features,
        sensitive_attrs=sensitive_attrs, qualified_attrs=qualified_attrs)
    rc.compile()

    clf_bin = open(clf_pickle,"rb")
    clf = pickle.load(clf_bin)
    dtc = DTCompiler(clf=clf, features=features, target=target, outfr=outfr, 
        fairness_targets=fairness_targets)
    dtc.extract()

    rc.frwrite(new=True)
    dtc.frwrite(new=False)

if __name__ == "__main__":
    dataset         = "tests/simple.csv"
    
    sensitive_attrs  = [("ethnicity",">",10)]
    qualified_attrs  = []
    fairness_targets = [("hire",">",0.5)]

    clf_pickle      = "classifiers/examples/decisiontree.pickle"
    features        = ["ethnicity", "colRank", "yExp"]
    target          = "hire"
    outfr           = "output/ex.fr"
    compile(dataset, clf_pickle, features, target, outfr, 
        sensitive_attrs, qualified_attrs, fairness_targets)