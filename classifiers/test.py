"""
__author__ = Yash Patel and Zachary Liu
__name__   = test.py
__description__ = Testing script for the classifier compilers
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from classifiers.decisiontree import DTCompiler

def test_decision_tree(X, y, X_labels, y_label):
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(X, y)
    dt_compiler = DTCompiler(clf, X_labels, y_label)
    result = dt_compiler.extract()
    print(result)

def test():
    data = pd.read_csv("tests/simple.csv")
    mat = np.transpose(data.as_matrix())
    
    X_labels = data.columns[:3]
    y_label  = data.columns[3]

    X = np.transpose(mat[:3])
    y = mat[3]
    
    test_decision_tree(X, y, X_labels, y_label)

if __name__ == "__main__":
    test()