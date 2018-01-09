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

import fairtear.compilers.constants as c

def _plot_fit(dataset, data, mu, std):
    """Plots the data and the Gaussian fit that was found. Results are saved
    according to the dataset, i.e. to output/[dataset]_fit.png

    Parameters
    ----------
    dataset : str
        String for the filename of the output

    data : Numpy array
        Raw data to be visualized (as bins)

    mu, std : float, float
        Parameters defining the fit Gaussian distribution
    """
    plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')

    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = scipy.stats.norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = "Fit results: mu={}, std={}".format(mu, std)
    plt.title(title)

    plt.savefig("output/{}_fit.png".format(dataset))
    plt.close()

def _entropy(data, to_plot=False):
    """Calculates entropy of the data once binned.

    Parameters
    ----------
    data : Numpy array
        Data for which entropy is to be calculated

    to_plot : bool
        Indicates whether the binning results are to be visualized. If True,
        the outputs are saved to output/partitions.png
    """
    num_partitions = 25
    counts, _ = np.histogram(data, num_partitions)
    probabilities = counts / len(data)
    if to_plot:
        plt.hist(data, bins=25, normed=True, alpha=0.6, color='g')
        plt.title("Data Partitions")
        plt.savefig("output/partitions.png")
        plt.close()
    return scipy.stats.entropy(probabilities)

def _step_fit(data, max_partitions=6):
    """Fits a step probability distribution to the data, i.e. distribution of the form
    [(0,1,.4),(1,2,.6)], which means the values will be in (0,1) w/ 40% 
    prob and (1,2) w/ 60%

    Parameters
    ----------
    data : Numpy array
        Data to be partitioned

    max_partitions : int
        Number of partitions in the final step result
    """
    min_dist         = None
    best_probs       = None
    best_partitions  = None

    for num_partitions in range(1,max_partitions):
        counts, partitions = np.histogram(data, num_partitions)
        probs = counts / len(data)
        
        def _step_cdf(x):
            cdf = 0.0
            for i in range(len(partitions)-1):
                if partitions[i] < x:
                    if x >= partitions[i+1]:
                        cdf += probs[i]
                    else:
                        cdf += ((x - partitions[i]) / (partitions[i+1] - partitions[i])) \
                            * probs[i]
                else: break
            return cdf

        step_cdf = np.vectorize(_step_cdf)
        step_dist, _ = scipy.stats.kstest(data, step_cdf)

        if min_dist is None or step_dist < min_dist:
            min_dist = step_dist
            best_probs = probs
            best_partitions = partitions

    # fix floating-point imprecision necessary in the final .fr file output
    for i in range(len(best_probs)-1):
        best_probs[i] = round(best_probs[i], c.DECIMAL_PRECISION)
    best_probs[-1] = 1 - sum(best_probs[:-1])

    fit = [(best_partitions[i],best_partitions[i+1],best_probs[i]) 
        for i in range(len(best_partitions)-1)]
    return fit, min_dist

def make_fit(data):
    """Given data, determines which fit is best and returns the parameters
    of this fit. Returns fit, fit_type, mse (mean-square-error) of whichever
    the best is. Currently, fits of the types:

    - gaussian : standard normal distribution (mu, std) params
    - step : tuples of fixed probabilities across ranges, i.e.
    [(0,1,.4),(1,2,.6)] means the values will be in (0,1) w/ 40% prob and (1,2) w/ 60%

    Parameters
    ----------
    data : Numpy array
        Data to be partitioned
    """
    gauss_fit  = scipy.stats.norm.fit(data)
    gauss_dist, _ = scipy.stats.kstest(data, "norm", args=gauss_fit)
    step_fit, step_dist = _step_fit(data, max_partitions=6)

    if gauss_dist < step_dist:
        return gauss_fit, "gaussian", gauss_dist
    return step_fit, "step", step_dist

def _partition(data, partition_data, partition):
    """Given data, partition data, and the current partition, returns the
    fit, fit_type, mse as the result. If mse is returned as None, this
    indicates that no partition is to be made, i.e. data should NOT be
    partitioned on the partition_data set. This occurs if insufficient
    information gain is made, the old MSE was lower than new (partitioned)
    MSE, or the partitions covered too little of the data. 

    If a partition WAS made, the fit and fit_type are each themselves
    tuples of the form (left_fit, right_fit) and (left_type, right_type).

    Parameters
    ----------
    data : Numpy array
        Data to be partitioned

    partition_data : Numpy array
        Array to be used for partitioning the data array
    
    partition : float
        Value where the partition data is to be split
    """
    orig_entropy = _entropy(data)
    left_partition  = data[partition_data <= partition]
    right_partition = data[partition_data > partition]
    
    left_frac  = len(left_partition)  / len(data)
    right_frac = len(right_partition) / len(data)
    
    new_entropy = left_frac * _entropy(left_partition) + \
        right_frac * _entropy(right_partition)
    information_gain = orig_entropy - new_entropy
    
    orig_fit, orig_type, orig_dist = make_fit(data)

    if information_gain < c.INFORMATION_GAIN_THRESH \
        or left_frac  < c.PARTITION_FRAC_THRESH     \
        or right_frac < c.PARTITION_FRAC_THRESH: 

        return orig_fit, orig_type, orig_dist, None

    # ===================== Fits on the partitioned data ===================== #
    fits, fit_types, dists = [orig_fit], [orig_type], [orig_dist]
    for values in [left_partition, right_partition]:
        fit, fit_type, dist = make_fit(values)

        fits.append(fit)
        fit_types.append(fit_type)
        dists.append(dist)

    orig_fit,  left_fit,  right_fit    = fits
    orig_type, left_type, right_type = fit_types
    orig_dist, left_dist, right_dist = dists
    new_dist = left_frac * left_dist + right_frac * right_dist
    
    # TODO: determine whether new_dist makes sense as a metric
    # if orig_dist < new_dist: 
    #     return orig_fit, orig_type, None
    return [left_fit, right_fit], [left_type, right_type], \
        new_dist, [left_partition, right_partition]

def _make_partition(data, partition_data):
    """Given data and the corresponding partitioning data, determines the best
    partition of the data based on partition_data. Returns a tuple of
    fit, fit_type, partition as the result. If fit is returned as None, this
    indicates that no partition is to be made, i.e. data should NOT be
    partitioned on the partition_data set
    
    Parameters
    ----------
    data : Numpy array
        Data to be partitioned

    partition_data : Numpy array
        Array to be used for partitioning the data array
    """
    considered_partitions = 5
    partition_mean = np.mean(partition_data)
    partition_std  = np.std(partition_data)
    potential_partition_vals = np.linspace(
        partition_mean - partition_std,
        partition_mean + partition_std,
        considered_partitions)

    min_dist  = None
    best_fit  = None
    best_fit_type  = None
    best_partition = None
    best_partition_val = None

    for partition_val in potential_partition_vals:
        fit, fit_type, dist, partition = _partition(data, partition_data, partition_val)
        if partition is not None:
            if min_dist is None or dist < min_dist:
                min_dist = dist
                best_fit = fit
                best_fit_type  = fit_type
                best_partition = partition
                best_partition_val = partition_val

    return best_fit, best_fit_type, best_partition_val, best_partition

def make_partitions(data, partition_data):
    max_partitions  = 5
    fits           = []
    fit_types      = []
    partition_vals = []
    partitions     = [data]

    for _ in range(max_partitions):
        partition_entropies = [_entropy(partition) for partition in partitions]
        to_partition_ind = np.argmax(partition_entropies)
        subdata           = partitions[to_partition_ind]
        partition_subdata = partition_data[subdata.index]

        fit, fit_type, partition_val, partition = _make_partition(subdata, partition_subdata)
        if fit is not None:
            fits = fits[:to_partition_ind] + fit + fits[to_partition_ind+1:]
            fit_types = fit_types[:to_partition_ind] + fit_type + fit_types[to_partition_ind+1:]
            partition_vals.insert(to_partition_ind, partition_val)
            partitions = partitions[:to_partition_ind] + partition + partitions[to_partition_ind+1:]
        else: break
    return fits, fit_types, partition_vals, partitions