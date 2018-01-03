"""
__author__ = Yash Patel and Zachary Liu
__name__   = test.py
__description__ = Testing script for the classifier compilers
"""

import pickle
import pprint
import pandas as pd
import numpy as np
import csv
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC

from decisiontree import DTCompiler
from svm import SVMCompiler

def _data_from_csv(x_csv, y_csv):
    """Extracts the X, y data columns and their corresponding labels (column headers) 
    from the csv and returns them as np arrays, as X, y, X_labels, y_label
    
    Parameters
    ----------
    x_csv : str
        Filename of the csv where the input dataset is stored
    """
    data = pd.read_csv(x_csv)

    X = data.as_matrix()
    with open(y_csv) as f:
        y = csv.reader(f).__next__()
    X_labels = list(data.columns)
    y_label  = 'income'

    return X, y, X_labels, y_label

def generate_clfs(X, y):
    """Generates clfs and stores them as pickle dumps in classifiers/examples/ 
    directory that are to predict from X -> y
    
    Parameters
    ----------
    X : Numpy matrix (2D)
        Input features to be used for prediction by the classifier

    y : Numpy array (1D)
        Target values to be predicted by the classifiers
    """
    clfs = [
        ("decisiontree", DecisionTreeClassifier(random_state=0)),
        ("svm", LinearSVC(random_state=0)),
    ]
    for clf_type, clf in clfs:
        clf.fit(X, y)
        pickle_out = open("classifiers/examples/adult_{}.pickle".format(clf_type),"wb")
        pickle.dump(clf, pickle_out)
        pickle_out.close()


def test_clfs(X_labels, y_label):
    """Tests the extraction of rules from the classifiers, using the feature
    and output label names
    
    Parameters
    ----------
    X_labels : Numpy matrix (2D)
        Input features that used to train clf. Must match columns from the input dataset

    y_label  : Numpy array (1D)
        Name of the clf target variable. Must match a column from the input dataset
    """
    compilers = [
        ("decisiontree", DTCompiler),
        ("svm", SVMCompiler),
    ]

    for compiler_type, compiler_class in compilers:
        pickle_in = open("classifiers/examples/adult_{}.pickle".format(compiler_type), "rb")
        clf = pickle.load(pickle_in)
        fairness_targets = [("income",">",0.5)]

        compiler = compiler_class(clf, X_labels, y_label, "output/adult_{}.fr".format(compiler_type), fairness_targets)
        compiler.extract()
        compiler.frwrite(True)

def generate_and_test():
    """Generates and tests the extraction of rules from them classifiers
    
    Parameters
    ----------
    None
    """
    X, y, X_labels, y_label = _data_from_csv(x_csv='data/adult.data.csv', y_csv='data/adult.data.labels.csv')
    generate_clfs(X, y)
    test_clfs(X_labels, y_label)

if __name__ == "__main__":
    generate_and_test()