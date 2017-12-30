"""
__author__ = Yash Patel and Zachary Liu
__name__   = generate.py
__description__ = File for generating datasets to be used for testing .fr file
generator. Generated files follow the decision-tree-like structure of FairSquare fr files
"""

import pandas as pd
import numpy as np

def generate(fr, fn):
    num_samples = 500
    columns = ["sex", "capital_gain", "age", "education_num"]

    data = pd.DataFrame()
    for column in columns:
        data[column] = np.zeros(num_samples)

    data["sex"] = np.random.normal(loc=1.0, scale=1.0, size=(num_samples))

    data["capital_gain"][data["sex"] < 1] = \
        np.random.normal(loc=568.4105, scale=24248365.5428, size=(num_samples))
    data["age"][(data["sex"] < 1) & (data["capital_gain"] < 7298.0000)] = \
        np.random.normal(loc=38.4208, scale=184.9151, size=(num_samples))
    data["education_num"][(data["sex"] < 1) & (data["capital_gain"] < 7298.0000)] = \
        np.random.normal(loc=10.0827, scale=6.5096, size=(num_samples))

    data["age"][(data["sex"] < 1) & (data["capital_gain"] >= 7298.0000)] = \
        np.random.normal(loc=38.8125, scale=193.4918, size=(num_samples))
    data["education_num"][(data["sex"] < 1) & (data["capital_gain"] >= 7298.0000)] = \
        np.random.normal(loc=10.1041, scale=6.1522, size=(num_samples))

    data["capital_gain"][data["sex"] >= 1] = \
        np.random.normal(loc=1329.3700, scale=69327473.1006, size=(num_samples))
    data["age"][(data["sex"] >= 1) & (data["capital_gain"] < 5178.0000)] = \
        np.random.normal(loc=38.6361, scale=187.2435, size=(num_samples))
    data["education_num"][(data["sex"] >= 1) & (data["capital_gain"] < 5178.0000)] = \
        np.random.normal(loc=10.0817, scale=6.4841, size=(num_samples))

    data["age"][(data["sex"] >= 1) & (data["capital_gain"] >= 5178.0000)] = \
        np.random.normal(loc=38.2668, scale=187.2747, size=(num_samples))
    data["education_num"][(data["sex"] >= 1) & (data["capital_gain"] >= 5178.0000)] = \
        np.random.normal(loc=10.0974, scale=7.1793, size=(num_samples))
    
    data.to_csv("tests/{}.csv".format(fn), index=False)

if __name__ == "__main__":
    fr = """
    sex = gaussian(1,1)
    if sex < 1:
        capital_gain = gaussian(568.4105, 24248365.5428)
        if capital_gain < 7298.0000:
            age = gaussian(38.4208, 184.9151)
            education_num = gaussian(10.0827, 6.5096)
        else:
            age = gaussian(38.8125, 193.4918)
            education_num = gaussian(10.1041, 6.1522)
    else:
        capital_gain = gaussian(1329.3700, 69327473.1006)
        if capital_gain < 5178.0000:
            age = gaussian(38.6361, 187.2435)
            education_num = gaussian(10.0817, 6.4841)
        else:
            age = gaussian(38.2668, 187.2747)
            education_num = gaussian(10.0974, 7.1793)
    sensitiveAttribute(sex < 1)
    """

    generate(fr, "ex")