"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

class DTCompiler:
    def __init__(self, clf, features, targets, outfr):
        """Constructs a DTCompiler object, to be used to extract the decision rules
        from the decision tree scikit-learn classifier

        Parameters
        ----------
        clf : scikit-learn Decision Tree Classifier
            Classifier trained on predicting from features -> target. Should already be
            trained when initializing

        features : list of str
            List of input features used to train clf. Must match columns from the input dataset

        targets : str
            Name of the clf target variable. Must match a column from the input dataset

        outfr : str
            Filename where the output (.fr file) is to be stored
        """
        self.clf = clf
        self.features = features
        self.targets  = targets
        self.outfr = outfr

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
            count_labels = zip(self.clf.tree_.value[node_index, 0], self.targets)
            node['name'] = ', '.join(('{} of {}'.format(int(count), label)
                                      for count, label in count_labels))
        else:
            feature = self.features[self.clf.tree_.feature[node_index]]
            threshold = self.clf.tree_.threshold[node_index]
            node['name'] = '{} > {}'.format(feature, threshold)
            left_index = self.clf.tree_.children_left[node_index]
            right_index = self.clf.tree_.children_right[node_index]
            node['children'] = [self._extract(right_index),
                                self._extract(left_index)]
        return node

    def extract(self):
        """Constructs structure of rules in a fit decision tree classifier

        Parameters
        ----------
        None
        """
        extracted = self._extract(node_index=0)
        return extracted

    def frwrite(self):
        """Writes the internally stored self.extracted extracted decision tree
        to the self.outfr file destination

        Parameters
        ----------
        None
        """
        print("Reading classifier into .fr format...")
        file_lines = ["def F():\n"]
        self._recursive_frwrite(self.program, file_lines, num_tabs=1)
        
        print("Writing final output...")
        with open(self.outfr, "w") as f:
            f.writelines(file_lines)
        print("Completed writing file to: {}".format(self.outfr))