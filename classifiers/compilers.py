"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

from sklearn.tree import _tree
import numpy as np

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
        extracted = self._extract_helper(node_index=0)
        file_lines = []
        self._recursive_frwrite(extracted, file_lines, num_tabs=0)
        return file_lines

class SVMCompiler(BaseCompiler):
    def _extract(self):
        coef = self.clf.coef_.flatten()
        assert(len(self.features) == len(coef))
        intercept = self.clf.intercept_[0]

        return [
            "{} = {}\n".format(self.target, " + ".join("{} * {}".format(feature, weight) for feature, weight in zip(self.features, coef))),
            "{} = {} + {}\n".format(self.target, self.target, intercept),
        ]
