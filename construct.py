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

def gaussian_mse(data, mu, std):
    counts, partitions = np.histogram(data, 25)
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
    information_gain = orig_entropy - new_entropy
    
    mus, stds, mses = [], [], []
    for values, dataset in zip([data, left_partition, right_partition], 
        ["original", "left", "right"]):
        
        mu, std = norm.fit(values)
        plot_fit(dataset, values, mu, std)
        mse = gaussian_mse(values, mu, std)

        mus.append(mu)
        stds.append(std)
        mses.append(mse)

    orig_mu, left_mu, right_mu    = mus
    orig_std, left_std, right_std = stds
    orig_mse, left_mse, right_mse = mses
    new_mse = left_frac * left_mse + right_frac * right_mse

    print("Information gain: {}".format(information_gain))
    print("MSEs: {} (Original) ; {} (New)".format(orig_mse, new_mse))

    if information_gain < c.INFORMATION_GAIN_THRESH or orig_mse < new_mse:
        return (orig_mu, orig_std), None
    return ((left_mu, left_std), (right_mu, right_std)), new_mse

def construct(csv):
    program = {}
    completed = set()

    df = pd.read_csv(csv)
    for i, partition_column in enumerate(df.columns):
        print("Running partitioning on: {}...".format(partition_column))
        if partition_column not in completed:
            data = df[partition_column]
            mu, std = norm.fit(data)
            program[partition_column] = {
                "fit" : (mu, std),
                "partitions" : {}
            }
            completed.add(partition_column)

            for j, column in enumerate(df.columns[i+1:]):
                partition_mean = np.mean(data)
                partition_std  = np.std(data)
                partitions = [partition_mean - partition_std, 
                    partition_mean, partition_mean + partition_std]

                min_mse  = None
                best_fit = None
                best_partition = None

                for partition in partitions:
                    fit, mse = run_partition(df, partition_column, column, partition)
                    if mse is not None:
                        if min_mse is None or mse < min_mse:
                            min_mse = mse
                            best_fit = fit
                            best_partition = partition

                if best_fit is not None:
                    left_fit, right_fit = best_fit
                    program[partition_column]["partitions"][partition] = {
                        "left" : {
                            column : {
                                "fit" : left_fit,
                                "partitions" : {}
                            }
                        },
                        "right" : {
                            column : {
                                "fit" : right_fit,
                                "partitions" : {}
                            }
                        }
                    }
                    completed.add(column)
    print("Compiled program tree!")
    return program

def test():
    program = construct("tests/ex.csv")
    print(program)

if __name__ == "__main__":
    fr_input = """
    ethnicity = gaussian(0,100)
    colRank = gaussian(25,100)
    yExp = gaussian(10,25)
    if ethnicity > 10:
        colRank = colRank + 5"""

    ex_output = {
        "ethnicity" : {
            "fit" : (0,100),
            "partitions" : {
                10 : {
                    "left" : {
                        "colRank" : {
                            "fit" : (25,100),
                            "partitions" : {}
                        }
                    },
                    "right" : {
                        "colRank" : {
                            "fit" : (30,100),
                            "partitions" : {}
                        }
                    }
                }
            }
        },
        "yExp" : {
            "fit" : (10,25),
            "partitions" : {}
        }
    }

    test()