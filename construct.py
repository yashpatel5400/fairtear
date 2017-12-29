"""
__author__ = Yash Patel and Zachary Liu
__name__   = construct.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import scipy.stats
import pandas as pd
import numpy as np

def plot_partitions(arr, partitions):
    plt.scatter(arr, np.ones(len(arr)))
    for partition in partitions:
        plt.axvline(partition)
    plt.savefig("output/partitions.png")
    plt.close()

def entropy(arr):
    num_partitions = 10

    arr_range = np.max(arr) - np.min(arr)
    step = arr_range / num_partitions
    partitions = [np.min(arr) + step * i for i in range(num_partitions+1)]
    probabilities = np.zeros(num_partitions)
    for i in range(num_partitions):
        if i != num_partitions - 1:
            inrange = arr[(arr >= partitions[i]) & (arr < partitions[i+1])]
        else:
            inrange = arr[(arr >= partitions[i]) & (arr <= partitions[i+1])]
        probabilities[i] = len(inrange) / len(arr)

    plot_partitions(arr, partitions)
    entropy = scipy.stats.entropy(probabilities)
    print("Entropy: {}".format(entropy))
    return entropy

def construct(csv):
    df = pd.read_csv(csv)

def test():
    test_arr = np.array([1] * 5 + [10] * 5)
    entropy(test_arr)
    test_arr = np.array(range(10))
    entropy(test_arr)

if __name__ == "__main__":
    test()