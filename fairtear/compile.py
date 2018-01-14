"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

# ratchet way of getting around namespace issues with FairSquare
import sys
if __name__ == "__main__":
    sys.path += ['fairtear/external/fairsquare/src']

import ast
import pickle
import pandas as pd
import numpy as np
import csv
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from fairtear.compilers.simple import SimpleCompiler
from fairtear.compilers.recursive import RecursiveCompiler
from fairtear.classifiers.base import Compiler
from fairtear.classifiers.test_adult import generate_clfs, data_from_csv

# FairSquare imports
from parse import Encoder
from fairProve import proveFairness

def load_csv(x_csv):
    df = pd.read_csv(x_csv)
    labels = list(df.columns)
    return df, labels

def compile(clf_pickle, x_csv, y_label, outfr, sensitive_attrs, 
    qualified_attrs, fairness_targets):
    """Main function, used to compile into the final .fr file. Takes the dataset and
    sensitive_attrs to construct the popModel() function and clf, features, and target
    for F(). Outputs are saved to the outfr destination (returns void)

    Parameters
    ----------
    clf_pickle : str
        Filename of where a pickled classifier is saved

    x_csv : DataFrame
        Filename of the csv where the input dataset is stored

    y_label : str
        Label of the target attribute

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
    df, labels = load_csv(x_csv)

    rc = RecursiveCompiler(df, maxdepth=2,
        sensitive_attrs=sensitive_attrs, qualified_attrs=qualified_attrs)
    rc.compile()

    with open(clf_pickle, "rb") as clf_bin:
        clf = pickle.load(clf_bin)
    compiler = Compiler(clf, labels, y_label, fairness_targets)
    
    with open(outfr, "w") as file:
        rc.frwrite(file)
    with open(outfr, "a") as file:
        compiler.frwrite(file)

def fair_prove(fn):
    f = open(fn, "r")
    node = ast.parse(f.read())

    e = Encoder()
    e.visit(node)

    print("\n\n== Population and program encoding == ")
    print("Population model: ", e.model)
    print("Program: ", e.program)

    print("Probability dists: ", e.vdist)
    print("fairness target", e.fairnessTarget)
    print("sensitiveAttribute", e.sensitiveAttribute)
    print("\n\n")

    output           = None
    epsilon          = 0.1
    finiteMaximize   = True
    randarg          = None
    infiniteMaximize = True
    plot             = False
    z3qe             = True
    numHists         = 5
    histBound        = 3
    timeoutarg       = None
    adapt            = False
    rotate           = False
    verbose          = True

    return proveFairness(e, output, epsilon, finiteMaximize, randarg, infiniteMaximize, 
            plot, z3qe, numHists, histBound, timeoutarg, adapt,
            rotate, verbose)

def test_compile():
    x_csv = "fairtear/data/adult.data.csv"
    y_csv = "fairtear/data/adult.data.labels.csv"

    X, y, X_labels, y_label = data_from_csv(x_csv=x_csv, y_csv=y_csv)
    generate_clfs(X, y)

    # ------------------------------------------------------------------------------

    fairness_targets = [("income",">",0.5)]
    sensitive_attrs  = [("ethnicity",">",10)]
    qualified_attrs  = []
    
    compilers = [
        # ("decisiontree", Compiler),
        ("svm", Compiler),
        # ("nn", Compiler),
    ]

    for compiler_type, compiler_class in compilers:
        clf_pickle = "fairtear/classifiers/examples/adult_{}.pickle".format(compiler_type)
        outfr = "fairtear/output/adult_{}.fr".format(compiler_type)
        y_label = "income"
        compile(clf_pickle, x_csv, y_label, outfr, sensitive_attrs, 
            qualified_attrs, fairness_targets)
        fair_prove(outfr)
        
if __name__ == "__main__":
    test_compile()
    fair_prove("fairtear/output/adult_decisiontree.fr")