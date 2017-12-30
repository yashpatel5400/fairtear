"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

class DTCompiler:
    def __init__(self, clf, features, targets):
        self.clf = clf
        self.features = features
        self.targets  = targets

    def _extract(self, node_index):
        """Structure of rules in a fit decision tree classifier"""
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
        return self._extract(node_index=0)