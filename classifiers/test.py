"""
__author__ = Yash Patel and Zachary Liu
__name__   = test.py
__description__ = Testing script for the classifier compilers
"""

import pickle
import pprint
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from classifiers.decisiontree import DTCompiler

def _data_from_csv(incsv):
    data = pd.read_csv(incsv)
    mat = np.transpose(data.as_matrix())

    X_labels = data.columns[:3]
    y_label  = data.columns[3]

    X = np.transpose(mat[:3])
    y = mat[3]
    return X, y, X_labels, y_label

def generate_clfs(X, y):
    clfs = [DecisionTreeClassifier(random_state=0)]
    clf_types = ["decisiontree"]
    for clf, clf_type in zip(clfs, clf_types):
        clf.fit(X, y)
        pickle_out = open("classifiers/examples/{}.pickle".format(clf_type),"wb")
        pickle.dump(clf, pickle_out)
        pickle_out.close()
        
def _test_decision_tree(X_labels, y_label):
    pickle_in = open("classifiers/examples/decisiontree.pickle","rb")
    clf = pickle.load(pickle_in)
    dt_compiler = DTCompiler(clf, X_labels, y_label, "recur_ex.fr")
    result = dt_compiler.extract()
    pprint.pprint(result)

def test_clfs(X_labels, y_label):
    _test_decision_tree(X_labels, y_label)

def generate_and_test():
    X, y, X_labels, y_label = _data_from_csv(incsv="tests/simple.csv")
    generate_clfs(X, y)
    test_clfs(X_labels, y_label)

if __name__ == "__main__":
    generate_and_test()