"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

# ratchet way of getting around namespace issues with FairSquare
import sys
import os.path
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'external/fairsquare/src'))

import ast
import pickle
import pandas as pd
import numpy as np
import csv
import json
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

def compile(clf_pickle, x_csv, y_label, outfr, sensitive_attrs, 
    qualified_attrs, fairness_targets, num_features=None):
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

    num_features : int (> 0)
        Number of features on which the classifier has been trained. This must be less than
        the total number of features in the dataset (no exception will be thrown in the case
        it exceeds the len: simply follows as the total dataset)
    """
    df = pd.read_csv(x_csv)
    labels = list(df.columns)
    if num_features is not None:
        labels = labels[:num_features]
        df = df[labels]

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
    verbose          = False

    return proveFairness(e, output, epsilon, finiteMaximize, randarg, infiniteMaximize, 
            plot, z3qe, numHists, histBound, timeoutarg, adapt,
            rotate, verbose)

def test_compile(num_features=None):
    x_csv = "fairtear/data/adult.data.csv"
    y_csv = "fairtear/data/adult.data.labels.csv"

    X, y, X_labels, y_label = data_from_csv(x_csv=x_csv, y_csv=y_csv)

    if num_features is not None:
        X        = X[:,:num_features]
        X_labels = X_labels[:num_features]
    generate_clfs(X, y)

    # ------------------------------------------------------------------------------

    fairness_targets = [("income",">",0.5)]
    sensitive_attrs  = [("age",">",35)]
    qualified_attrs  = []
    
    compilers = [
        ("decisiontree", Compiler),
        ("svm", Compiler),
        ("nn", Compiler),
    ]

    for compiler_type, compiler_class in compilers:
        clf_pickle = "fairtear/classifiers/examples/adult_{}.pickle".format(compiler_type)
        outfr = "fairtear/output/adult_{}.fr".format(compiler_type)
        y_label = "income"
        compile(clf_pickle, x_csv, y_label, outfr, sensitive_attrs, 
           qualified_attrs, fairness_targets, num_features=num_features)
        fair_prove(outfr)
        
if __name__ == "__main__":
    if len(sys.argv) == 1:
        test_compile(num_features=4)
        sys.exit()

    args = json.loads(sys.argv[1])
    compile(**args)
    fair_prove(args["outfr"])
