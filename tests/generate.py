"""
__author__ = Yash Patel and Zachary Liu
__name__   = generate.py
__description__ = File for generating datasets to be used for testing .fr file
generator. Generated files follow the decision-tree-like structure of FairSquare fr files
"""

import pandas as pd
import numpy as np

def generate(fr, fn):
    num_samples = 100

    data = pd.DataFrame()
    data["ethnicity"] = np.random.normal(loc=0.0, scale=100.0, size=(num_samples))
    data["colRank"]   = np.random.normal(loc=25.0, scale=100.0,size=(num_samples))
    data["yExp"]      = np.random.normal(loc=10.0, scale=25.0, size=(num_samples))
    data["colRank"][data["ethnicity"] > 10] += 5
    
    data.to_csv("tests/{}.csv".format(fn), index=False)

if __name__ == "__main__":
    fr = """
    ethnicity = gaussian(0,100)
    colRank = gaussian(25,100)
    yExp = gaussian(10,25)
    if ethnicity > 10:
        colRank = colRank + 5
    """
    generate(fr, "ex")