"""
__author__ = Yash Patel and Zachary Liu
__name__   = helper.py
__description__ = Set of helper functions used for all the .fr compilers, including
plotting and metric calculations
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import scipy.stats
import numpy as np
import math

import compilers.constants as c

def _plot_fit(dataset, data, mu, std):
    plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')

    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = scipy.stats.norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = "Fit results: mu={}, std={}".format(mu, std)
    plt.title(title)

    plt.savefig("output/{}_fit.png".format(dataset))
    plt.close()

def _entropy(data, to_plot=True):
    num_partitions = 10
    counts, _ = np.histogram(data, 25)
    probabilities = counts / len(data)
    if to_plot:
        plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')
        plt.title("Data Partitions")
        plt.savefig("output/partitions.png")
        plt.close()

    return scipy.stats.entropy(probabilities)

def _gaussian_mse(data, mu, std):
    counts, partitions = np.histogram(data, 25)
    dist = scipy.stats.norm(mu, std)
    predicted_counts = np.array([dist.pdf(np.mean([partitions[i],partitions[i+1]])) * len(data) 
        for i in range(len(partitions)-1)])
    return np.square(counts - predicted_counts).mean()

def _step_fit(data, max_partitions=6):
    min_avg_mse      = None
    best_counts      = None
    best_partitions  = None

    for num_partitions in range(1,max_partitions):
        counts, partitions = np.histogram(data, num_partitions)
        total_mse = 0
        for i in range(len(partitions)-1):
            in_part = data[(partitions[i] <= data) & (data < partitions[i+1])]
            partition_mid = np.mean([partitions[i],partitions[i+1]])
            total_mse += np.square(in_part - partition_mid).mean()
        avg_mse = total_mse / num_partitions

        if min_avg_mse is None or avg_mse < min_avg_mse:
            min_avg_mse = avg_mse
            best_counts = counts
            best_partitions = partitions

    probabilities = best_counts / len(data)
    mse = min_avg_mse * len(best_counts)
    fit = list(zip(best_partitions, probabilities))
    return fit, mse

def _partition(data, partition_data, partition):
    orig_entropy = _entropy(data)
    left_partition  = data[partition_data <= partition]
    right_partition = data[partition_data > partition]
    
    left_frac  = len(left_partition)  / len(data)
    right_frac = len(right_partition) / len(data)
    
    new_entropy = left_frac * _entropy(left_partition) + \
        right_frac * _entropy(right_partition)
    information_gain = orig_entropy - new_entropy
    
    fits, mses = [], []
    for values, dataset in zip([data, left_partition, right_partition], 
        ["original", "left", "right"]):
        
        gauss_fit = scipy.stats.norm.fit(values)
        gauss_mse = _gaussian_mse(values, mu, std)
        step_fit, step_mse = _step_fit(data, max_partitions=6)

        if gauss_mse < step_mse:
            fits.append(gauss_fit)
            mses.append(gauss_mse)
        else:
            fits.append(step_fit)
            mses.append(step_mse)

    orig_fit, left_fit, right_fit = fits
    orig_mse, left_mse, right_mse = mses
    new_mse = left_frac * left_mse + right_frac * right_mse

    print("Information gain: {}".format(information_gain))
    print("MSEs: {} (Original) ; {} (New)".format(orig_mse, new_mse))

    if information_gain < c.INFORMATION_GAIN_THRESH \
        or left_frac  < c.PARTITION_FRAC_THRESH     \
        or right_frac < c.PARTITION_FRAC_THRESH     \
        or orig_mse < new_mse:
        
        return orig_fit, None
    return (left_fit, right_fit), new_mse

def make_partition(data, partition_data, num_partitions=5):
    partition_mean = np.mean(partition_data)
    partition_std  = np.std(partition_data)
    partitions = np.linspace(
        partition_mean - partition_std,
        partition_mean + partition_std,
        num_partitions)

    min_mse  = None
    best_fit = None
    best_partition = None

    for partition in partitions:
        fit, mse = _partition(data, partition_data, partition)
        if mse is not None:
            if min_mse is None or mse < min_mse:
                min_mse = mse
                best_fit = fit
                best_partition = partition
    return best_fit, best_partition