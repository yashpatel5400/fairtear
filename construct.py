"""
__author__ = Yash Patel and Zachary Liu
__name__   = construct.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm

import scipy.stats
import pandas as pd
import numpy as np
import math

import constants as c

def plot_fit(dataset, data, mu, std):
    # Plot the PDF.
    plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')

    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = "Fit results: mu={}, std={}".format(mu, std)
    plt.title(title)

    plt.savefig("output/{}_fit.png".format(dataset))
    plt.close()

def entropy(data, to_plot=True):
    num_partitions = 10

    arr_range = np.max(data) - np.min(data)
    step = arr_range / num_partitions
    partitions = np.histogram(data, 25)[0]
    probabilities = partitions / len(data)

    if to_plot:
        plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')
        plt.title("Data Partitions")
        plt.savefig("output/partitions.png")
        plt.close()

    entropy = scipy.stats.entropy(probabilities)
    return entropy

def gaussian_fit_mse(data, dataset):
    counts, partitions = np.histogram(data, 25)
    mu, std = norm.fit(data)
    plot_fit(dataset, data, mu, std)
    dist = scipy.stats.norm(mu, std)

    predicted_counts = np.array([dist.pdf(np.mean([partitions[i],partitions[i+1]])) * len(data) 
        for i in range(len(partitions)-1)])
    return np.square(counts - predicted_counts).mean()

def run_partition(df, partition_column, column, partition):
    data = df[column]
    orig_entropy = entropy(data)
    left_partition  = data[df[partition_column] <= partition]
    left_frac = len(left_partition) / len(data)
    right_partition = data[df[partition_column] > partition]
    right_frac = len(right_partition) / len(data)
    
    new_entropy = left_frac * entropy(left_partition) + \
        right_frac * entropy(right_partition)

    information_gain = new_entropy - orig_entropy
    if information_gain < c.INFORMATION_GAIN_THRESH:
        return None

    orig_mse  = gaussian_fit_mse(data, "original")
    left_mse  = gaussian_fit_mse(left_partition, "left")
    right_mse = gaussian_fit_mse(right_partition, "right")
    new_mse = left_frac * left_mse + right_frac * right_mse

    if orig_mse < new_mse:
        return None

def construct(csv):
    df = pd.read_csv(csv)
    for i, partition_column in enumerate(df.columns):
        for j, column in enumerate(df.columns[i+1:]):
            partition_mean = np.mean(df[partition_column])
            partition_std  = np.std(df[partition_column])
            partitions = [partition_mean - partition_std, 
                partition_mean, partition_mean + partition_std]

            for partition in partitions:
                run_partition(df, partition_column, column, partition)

def test():
    test_arr = np.array([1] * 5 + [10] * 5)
    entropy(test_arr)
    construct("tests/ex.csv")

if __name__ == "__main__":
    test()