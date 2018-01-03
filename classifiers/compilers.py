"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
import numpy as np
import math

from base import BaseCompiler

class DTCompiler(BaseCompiler):
    def _extract_helper(self, node_index):
        """Helper function to constructs structure of rules in a fit 
        decision tree classifier (for a single layer)

        Parameters
        ----------
        node_index : int
            Index of the depth of the node being extracted from the decision tree
        """
        node = {}
        if self.clf.tree_.children_left[node_index] == -1:  # indicates leaf
            node["name"] = [int(count) for count in self.clf.tree_.value[node_index, 0]]
        else:
            feature = self.features[self.clf.tree_.feature[node_index]]
            threshold = self.clf.tree_.threshold[node_index]
            node["name"] = "{} > {}".format(feature, threshold)
            left_index   = self.clf.tree_.children_left[node_index]
            right_index  = self.clf.tree_.children_right[node_index]
            node["children"] = [self._extract_helper(right_index),
                                self._extract_helper(left_index)]
        return node

    def _recursive_frwrite(self, extracted, file_lines, num_tabs):
        tabs = "\t" * num_tabs
        
        # case of reaching a leaf node
        if "children" not in extracted:
            label_counts = extracted["name"]
            best_label = np.argmax(label_counts)
            file_lines.append("{}{} = {}\n".format(tabs, self.target, best_label))
        else:
            conditional = extracted["name"]
            left, right = extracted["children"]
            
            file_lines.append("{}if {}:\n".format(tabs, conditional))
            self._recursive_frwrite(left,file_lines,num_tabs+1)
            file_lines.append("{}else:\n".format(tabs))
            self._recursive_frwrite(right,file_lines,num_tabs+1)

    def _extract(self):
        """Constructs structure of rules in a fit decision tree classifier

        Parameters
        ----------
        None
        """
        assert(isinstance(self.clf, DecisionTreeClassifier))

        extracted = self._extract_helper(node_index=0)
        file_lines = []
        self._recursive_frwrite(extracted, file_lines, num_tabs=0)
        return file_lines

class SVMCompiler(BaseCompiler):
    def _extract(self):
        assert(isinstance(self.clf, LinearSVC))

        coef = self.clf.coef_.flatten()
        assert(len(self.features) == len(coef))
        intercept = self.clf.intercept_[0]

        return [
            "{} = {}\n".format(self.target, " + ".join("{} * {}".format(feature, weight) for feature, weight in zip(self.features, coef))),
            "{} = {} + {}\n".format(self.target, self.target, intercept),
        ]

class NNCompiler(BaseCompiler):
    def _extract(self):
        assert(isinstance(self.clf, MLPClassifier))

        prev_features = list(self.features)
        next_features = []
        output = []
        debug_output_layer_count = 0

        for layer_i, (coef, intercepts) in enumerate(zip(self.clf.coefs_, self.clf.intercepts_)):
            assert(coef.shape[0] == len(prev_features))
            assert(coef.shape[1] == len(intercepts))

            is_output_layer = (layer_i == self.clf.n_layers_ - 2)
            if is_output_layer:
                debug_output_layer_count += 1

            for neuron_i, (weights, intercept) in enumerate(zip(coef.T, intercepts)):
                if is_output_layer:
                    assert(neuron_i == 0)
                    name = self.target
                else:
                    name = "hidden_{}_{}".format(layer_i, neuron_i)

                expression = " + ".join("{} * {}".format(feature, weight) for feature, weight in zip(prev_features, weights))
                next_features.append(name)
                output.append("{} = {}\n".format(name, expression))
                output.append("{} = {} + {}\n".format(name, name, intercept))

                activation = self.clf.out_activation_ if is_output_layer else self.clf.activation
                if activation == "relu":
                    output.append("if {} < 0:\n".format(name))
                    output.append("\t{} = 0\n".format(name))
                elif activation == "logistic":
                    output.append("{} = 1 / (1 + {} ** -{})\n".format(name, math.e, name))
                else:
                    raise Exception("Unsupported activation function: {}".format(activation))

            prev_features = next_features
            next_features = []

        assert(debug_output_layer_count == 1)

        # Shift to center around 0.5 instead of around 0
        output.append("{} = {} + 0.5\n".format(self.target, self.target))

        return output
