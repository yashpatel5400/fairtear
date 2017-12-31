"""
__author__ = Yash Patel and Zachary Liu
__name__   = decisiontree.py
__description__ = DTCompiler class that compiles a decision tree into the rule-based
structure of FairSquare
"""

class DTCompiler:
    def __init__(self, clf, features, target, outfr):
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
        """
        self.clf = clf
        self.features = features
        self.target   = target
        self.outfr    = outfr
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
            count_labels = zip(self.clf.tree_.value[node_index, 0], self.target)
            node["name"] = [(int(count), label) for count, label in count_labels]
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
        print(self.extracted)

    def _recursive_frwrite(self, extracted, file_lines, num_tabs):
        tabs = "\t" * num_tabs
        
        # case of reaching a leaf node
        if "children" not in extracted:
            label_counts = extracted["name"]
            print(max(label_counts)[1])
            best_label = max(label_counts)[1]
            file_lines.append("{}hire = {}\n".format(tabs, best_label))
        else:
            conditional = extracted["name"]
            left, right = extracted["children"]
            
            file_lines.append("{}{}:\n".format(tabs, conditional))
            self._recursive_frwrite(left,file_lines,num_tabs+1)
            file_lines.append("{}else:\n".format(tabs))
            self._recursive_frwrite(right,file_lines,num_tabs+1)

    def frwrite(self):
        """Writes the internally stored self.extracted extracted decision tree
        to the self.outfr file destination

        Parameters
        ----------
        None
        """
        print("Reading classifier into .fr format...")
        file_lines = ["def F():\n"]
        self._recursive_frwrite(self.extracted, file_lines, num_tabs=1)
        
        print("Writing final output...")
        with open(self.outfr, "w") as f:
            f.writelines(file_lines)
        print("Completed writing file to: {}".format(self.outfr))