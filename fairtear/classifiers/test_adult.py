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
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from fairtear.classifiers.base import Compiler

def data_from_csv(x_csv, y_csv):
    """Extracts the X, y data columns and their corresponding labels (column headers) 
    from the csv and returns them as np arrays, as X, y, X_labels, y_label
    
    Parameters
    ----------
    x_csv : str
        Filename of the csv where the input dataset is stored
    """
    X, X_labels = X_from_csv(x_csv)

    with open(y_csv) as f:
        y = csv.reader(f).__next__()
    y_label  = "income"

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
        ("nn", MLPClassifier(hidden_layer_sizes=(10, 10), random_state=0)),
    ]
    for clf_type, clf in clfs:
        print("Training {} classifier...".format(clf_type))
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            (clf_type, clf),
        ])
        pipeline.fit(X, y)
        print("Saving {} classifier...".format(clf_type))
        pickle_out = open("fairtear/classifiers/examples/adult_{}.pickle".format(clf_type),"wb")
        pickle.dump(pipeline, pickle_out)
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
        ("decisiontree", Compiler),
        ("svm", Compiler),
        ("nn", Compiler),
    ]

    for compiler_type, compiler_class in compilers:
        pickle_in = open("fairtear/classifiers/examples/adult_{}.pickle".format(
            compiler_type), "rb")
        clf = pickle.load(pickle_in)
        fairness_targets = [("income",">",0.5)]

        compiler = compiler_class(clf, X_labels, y_label, fairness_targets)
        with open("fairtear/output/adult_{}.fr".format(compiler_type), "w") as file:
            compiler.frwrite(file)

def generate_and_test():
    """Generates and tests the extraction of rules from them classifiers
    
    Parameters
    ----------
    None
    """
    X, y, X_labels, y_label = data_from_csv(
        x_csv="fairtear/data/adult.data.csv", 
        y_csv="fairtear/data/adult.data.labels.csv")
    generate_clfs(X, y)
    test_clfs(X_labels, y_label)

if __name__ == "__main__":
    generate_and_test()