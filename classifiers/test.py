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
    """Extracts the X, y data columns and their corresponding labels (column headers) 
    from the csv and returns them as np arrays, as X, y, X_labels, y_label
    
    Parameters
    ----------
    incsv : str
        Filename of the csv where the input dataset is stored
    """
    data = pd.read_csv(incsv)
    mat = np.transpose(data.as_matrix())

    X_labels = data.columns[:3]
    y_label  = [1,0]

    X = np.transpose(mat[:3])
    y = mat[3]
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
    clfs = [DecisionTreeClassifier(random_state=0)]
    clf_types = ["decisiontree"]
    for clf, clf_type in zip(clfs, clf_types):
        clf.fit(X, y)
        pickle_out = open("classifiers/examples/{}.pickle".format(clf_type),"wb")
        pickle.dump(clf, pickle_out)
        pickle_out.close()
        
def _test_decision_tree(X_labels, y_label):
    """Tests the extraction of rules from the DT classifier. The classifier dump must
    be stored at classifiers/examples/decisiontree.pickle
    
    Parameters
    ----------
    X_labels : Numpy matrix (2D)
        Input features that used to train clf. Must match columns from the input dataset

    y_label  : Numpy array (1D)
        Name of the clf target variable. Must match a column from the input dataset
    """
    pickle_in = open("classifiers/examples/decisiontree.pickle","rb")
    clf = pickle.load(pickle_in)
    dt_compiler = DTCompiler(clf, X_labels, y_label, "output/ex.fr")
    dt_compiler.extract()
    dt_compiler.frwrite()

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
    _test_decision_tree(X_labels, y_label)

def generate_and_test():
    """Generates and tests the extraction of rules from them classifiers
    
    Parameters
    ----------
    None
    """
    X, y, X_labels, y_label = _data_from_csv(incsv="tests/simple.csv")
    generate_clfs(X, y)
    test_clfs(X_labels, y_label)

if __name__ == "__main__":
    generate_and_test()