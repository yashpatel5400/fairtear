"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

from sklearn.tree import _tree
import numpy as np

class DTCompiler:
    def __init__(self, clf, features, target, outfr, fairness_targets):
        """Constructs a DTCompiler object, to be used to extract the decision rules
        from the decision tree scikit-learn classifier

        Parameters
        ----------
        clf : scikit-learn Decision Tree Classifier
            Classifier trained on predicting from features -> target. Should already be
            trained when initializing

        features : list of str
            List of input features used to train clf. Must match columns from the input dataset

        target : str
            Name of the clf target variable. Must match a column from the input dataset

        outfr : str
            Filename where the output (.fr file) is to be stored

        fairness_targets : list of (str,str,int) tuples
            List of the names of attributes to set desired fairness criterion. Each attr has a
            "threshold" value, and the second param MUST either be ">" or "<". Here 
            ("hire",">",0.5) corresponds to wanting to ensure the population satisfies hire > 0.5
            independent of sensitive attributes
        """
        self.clf = clf
        self.features = features
        self.target   = target
        self.outfr    = outfr
        self.fairness_targets = fairness_targets
        self.extracted = None

    def _extract(self, node_index):
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
            node["children"] = [self._extract(right_index),
                                self._extract(left_index)]
        return node

    def extract(self):
        """Constructs structure of rules in a fit decision tree classifier

        Parameters
        ----------
        None
        """
        print("Extracting rule-based classifier...")
        self.extracted = self._extract(node_index=0)
        
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

    def frwrite(self, new):
        """Writes the internally stored self.extracted extracted decision tree
        to the self.outfr file destination

        Parameters
        ----------
        new : bool
            Indicates whether this is a new file being written to or if being
            appended to an existing one
        """
        print("Reading classifier into .fr format...")
        file_lines = ["def F():\n"]
        self._recursive_frwrite(self.extracted, file_lines, num_tabs=1)
        
        for fairness_target, comp, thresh in self.fairness_targets:
            file_lines.append("\tfairnessTarget({} {} {})\n".format(
                fairness_target, comp, thresh))

        file_lines.append("\n")
        print("Writing final output...")

        if new:
            f = open(self.outfr, "w")
        else:
            f = open(self.outfr, "a")

        f.writelines(file_lines)
        f.close()
        print("Completed writing file to: {}".format(self.outfr))