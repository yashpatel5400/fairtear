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

def _entropy(data, to_plot=True):
    """Calculates entropy of the data once binned.

    Parameters
    ----------
    data : Numpy array
        Data for which entropy is to be calculated

    to_plot : bool
        Indicates whether the binning results are to be visualized. If True,
        the outputs are saved to output/partitions.png
    """
    num_partitions = 10
    counts, _ = np.histogram(data, 25)
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
    max_gof          = None
    best_probs       = None
    best_partitions  = None

    for num_partitions in range(1,max_partitions):
        counts, partitions = np.histogram(data, num_partitions)
        probs = counts / len(data)
        
        def _step_cdf(x):
            cdf = 0.0
            for i in range(len(partitions)):
                if partitions[i] < x:
                    if x >= partitions[i+1]:
                        cdf += probs[i]
                    else:
                        cdf += ((x - partitions[i]) / (partitions[i+1] - partitions[i])) \
                            * probs[i]
                else: break
            return cdf
        step_cdf = np.vectorize(_step_cdf)
        step_gof, _ = scipy.stats.kstest(data, step_cdf)

        print("Partitions: {}; GOF: {}".format(num_partitions, step_gof))
        if max_gof is None or max_gof < step_gof:
            max_gof = step_gof
            best_probs = probs
            best_partitions = partitions

    fit = [(best_partitions[i],best_partitions[i+1],best_probs[i]) 
        for i in range(len(best_partitions)-1)]
    return fit, max_gof

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
    gauss_fit = scipy.stats.norm.fit(data)
    gauss_gof, _ = scipy.stats.kstest(data, "norm", gauss_fit)
    step_fit, step_gof = _step_fit(data, max_partitions=6)

    print("Gaussian GOF: {}, Step GOF: {}".format(gauss_gof, step_gof))
    if gauss_gof > step_gof:
        return gauss_fit, "gaussian", gauss_gof
    return step_fit, "step", step_gof

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
    
    orig_fit, orig_type, orig_gof = make_fit(data)

    if information_gain < c.INFORMATION_GAIN_THRESH \
        or left_frac  < c.PARTITION_FRAC_THRESH     \
        or right_frac < c.PARTITION_FRAC_THRESH: 

        return orig_fit, orig_type, None

    # ===================== Fits on the partitioned data ===================== #
    fits, fit_types, gofs = [orig_fit], [orig_type], [orig_gof]
    for values in [left_partition, right_partition]:
        fit, fit_type, gof = make_fit(values)

        fits.append(fit)
        fit_types.append(fit_type)
        gofs.append(gof)

    orig_fit, left_fit, right_fit    = fits
    orig_type, left_type, right_type = fit_types
    orig_gof, left_gof, right_gof    = gofs
    new_gof = left_frac * left_gof + right_frac * right_gof

    print("Information gain: {}".format(information_gain))
    print("GOFs: {} (Original) ; {} (New)".format(orig_gof, new_gof))

    if orig_gof > new_gof: 
        return orig_fit, orig_type, None
    return (left_fit, right_fit), (left_type, right_type), new_gof

def make_partition(data, partition_data, num_partitions=5):
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
    
    num_partitions : int
        Number of legal partitions to be considered
    """
    partition_mean = np.mean(partition_data)
    partition_std  = np.std(partition_data)
    partitions = np.linspace(
        partition_mean - partition_std,
        partition_mean + partition_std,
        num_partitions)

    max_gof  = None
    best_fit = None
    best_fit_type  = None
    best_partition = None

    for partition in partitions:
        fit, fit_type, gof = _partition(data, partition_data, partition)
        if gof is not None:
            if max_gof is None or gof > max_gof:
                max_gof = gof
                best_fit = fit
                best_fit_type  = fit_type
                best_partition = partition
    return best_fit, best_fit_type, best_partition