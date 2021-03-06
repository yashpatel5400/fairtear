"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np
import math

def extract_decision_tree(clf, features, target):
    """Constructs structure of rules in a fit decision tree classifier

    Parameters
    ----------
    None
    """

    def _extract_helper(node_index):
        """Helper function to constructs structure of rules in a fit 
        decision tree classifier (for a single layer)

        Parameters
        ----------
        node_index : int
            Index of the depth of the node being extracted from the decision tree
        """
        node = {}
        if clf.tree_.children_left[node_index] == -1:  # indicates leaf
            node["name"] = [int(count) for count in clf.tree_.value[node_index, 0]]
        else:
            feature = features[clf.tree_.feature[node_index]]
            threshold = clf.tree_.threshold[node_index]
            node["name"] = "{} > {:.4f}".format(feature, threshold)
            left_index   = clf.tree_.children_left[node_index]
            right_index  = clf.tree_.children_right[node_index]
            node["children"] = [_extract_helper(right_index),
                                _extract_helper(left_index)]
        return node

    def _recursive_frwrite(extracted, file_lines, num_tabs):
        tabs = "\t" * num_tabs
        
        # case of reaching a leaf node
        if "children" not in extracted:
            label_counts = extracted["name"]
            best_label = np.argmax(label_counts)
            file_lines.append("{}{} = {}\n".format(tabs, target, best_label))
        else:
            conditional = extracted["name"]
            left, right = extracted["children"]
            
            file_lines.append("{}if {}:\n".format(tabs, conditional))
            _recursive_frwrite(left,file_lines,num_tabs+1)
            file_lines.append("{}else:\n".format(tabs))
            _recursive_frwrite(right,file_lines,num_tabs+1)

    assert(isinstance(clf, DecisionTreeClassifier))

    extracted = _extract_helper(node_index=0)
    file_lines = []
    _recursive_frwrite(extracted, file_lines, num_tabs=0)
    return [target], file_lines


def extract_svm(clf, features, target):
    assert(isinstance(clf, LinearSVC))

    coef = clf.coef_.flatten()
    assert(len(features) == len(coef))
    intercept = clf.intercept_[0]

    return [target], [
        "{} = {}\n".format(target, " + ".join("{} * {:.4f}".format(feature, weight) for feature, weight in zip(features, coef))),
        "{} = {} + {:.4f}\n".format(target, target, intercept),
    ]


def extract_neural_network(clf, features, target):
    assert(isinstance(clf, MLPClassifier))

    prev_features = list(features)
    next_features = []
    output = []
    debug_output_layer_count = 0

    for layer_i, (coef, intercepts) in enumerate(zip(clf.coefs_, clf.intercepts_)):
        assert(coef.shape[0] == len(prev_features))
        assert(coef.shape[1] == len(intercepts))

        is_output_layer = (layer_i == clf.n_layers_ - 2)
        if is_output_layer:
            debug_output_layer_count += 1

        for neuron_i, (weights, intercept) in enumerate(zip(coef.T, intercepts)):
            if is_output_layer:
                assert(neuron_i == 0)
                name = target
            else:
                name = "hidden_{}_{}".format(layer_i, neuron_i)

            expression = " + ".join("{} * {:.4f}".format(feature, weight) for feature, weight in zip(prev_features, weights))
            next_features.append(name)
            output.append("{} = {}\n".format(name, expression))
            output.append("{} = {} + {:.4f}\n".format(name, name, intercept))

            if not is_output_layer:
                if clf.activation == "relu":
                    output.append("if {} < 0:\n".format(name))
                    output.append("\t{} = 0\n".format(name))
                else:
                    raise Exception("Unsupported activation function: {}".format(activation))

        prev_features = next_features
        next_features = []

    assert(debug_output_layer_count == 1)

    return [target], output


def extract_scaler(clf, features, target):
    assert(isinstance(clf, StandardScaler))
    print("{} == {}".format(len(features), len(clf.scale_)))
    assert(len(features) == len(clf.scale_))
    assert(len(features) == len(clf.mean_))

    new_features = ["scaled_{}".format(feature) for feature in features]
    output = []
    for new_feature, feature, mean, scale in zip(new_features, features, clf.mean_, clf.scale_):
        output.append("{} = ({} - {:.4f}) * {:.4f}\n".format(new_feature, feature, mean, scale))
    return new_features, output


def extract_pipeline(clf, features, target):
    assert(isinstance(clf, Pipeline))

    output = []
    for _, next_clf in clf.steps:
        features, next_output = extract(next_clf, features, target)
        output += next_output

    return features, output


def extract(clf, features, target):
    extractors = {
        DecisionTreeClassifier: extract_decision_tree,
        LinearSVC: extract_svm,
        MLPClassifier: extract_neural_network,
        StandardScaler: extract_scaler,
        Pipeline: extract_pipeline,
    }
    extractor = None
    for sklearn_class, extractor_function in extractors.items():
        if isinstance(clf, sklearn_class):
            extractor = extractor_function
            break
    if extractor is None:
        raise Exception('Unsupported classifier type: {}'.format(clf.__class__.__name__))

    return extractor_function(clf, features, target)
