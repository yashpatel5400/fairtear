"""
__author__ = Yash Patel and Zachary Liu
__name__   = base.py
__description__ = BaseCompiler class with common logic to compile a classifier to rule-based
structure of FairSquare
"""

import numpy as np
from abc import ABC, abstractmethod

class BaseCompiler(ABC):
    def __init__(self, clf, features, target, fairness_targets):
        """Constructs a BaseCompiler object, to be used to extract the decision rules
        from the decision tree scikit-learn classifier

        Parameters
        ----------
        clf : scikit-learn Classifier
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
        self.fairness_targets = fairness_targets

    @abstractmethod
    def _extract(self):
        """Constructs structure of rules in a fit decision tree classifier

        Parameters
        ----------
        None
        """
        pass

    def frwrite(self, file):
        """Writes the extracted rules to the self.outfr file destination

        Parameters
        ----------
        new : bool
            Indicates whether this is a new file being written to or if being
            appended to an existing one
        """
        print("Reading classifier into .fr format...")
        file_lines = ["def F():\n"]
        file_lines += ['\t' + line for line in self._extract()]

        for fairness_target, comp, thresh in self.fairness_targets:
            file_lines.append("\tfairnessTarget({} {} {})\n".format(
                fairness_target, comp, thresh))

        print("Writing final output...")
        file.writelines(file_lines)
        print("Completed writing file to: {}".format(file.name))
