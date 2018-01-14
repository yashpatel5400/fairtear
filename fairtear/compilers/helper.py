"""
__author__ = Yash Patel and Zachary Liu
__name__   = helper.py
__description__ = Set of helper functions used for all the .fr compilers, including
plotting and metric calculations
"""

# fix floating point imprecision for probability calculations
import decimal
from decimal import Decimal

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import scipy.stats
import numpy as np
import math

import fairtear.compilers.constants as c
# decimal.getcontext().prec = c.DECIMAL_PRECISION

def _entropy(data):
    """Calculates entropy of the data once binned.

    Parameters
    ----------
    data : Numpy array
        Data for which entropy is to be calculated
    """
    num_partitions = 25
    counts, _ = np.histogram(data, num_partitions)
    probabilities = counts / len(data)
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
    dec_round = lambda x : Decimal(str(x)).quantize(
        Decimal(c.DECIMAL_FORMAT_STR), rounding=decimal.ROUND_UP)
    rounded_probs = [dec_round(prob) for prob in best_probs]
    rounded_probs[-1] = Decimal(1.0) - sum(rounded_probs[:-1])

    fit = [(best_partitions[i],best_partitions[i+1],float(rounded_probs[i])) 
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
        return gauss_fit, "gaussian"
    return step_fit, "step"

def _partition(data, orig_entropy, partition_data, partition):
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
    left_partition  = data[partition_data <= partition]
    right_partition = data[partition_data > partition]
    
    left_frac  = len(left_partition)  / len(data)
    right_frac = len(right_partition) / len(data)
    
    left_entropy  = _entropy(left_partition)
    right_entropy = _entropy(right_partition)

    new_entropy = left_frac * left_entropy + right_frac * right_entropy
    information_gain = orig_entropy - new_entropy

    if information_gain < c.INFORMATION_GAIN_THRESH \
        or left_frac    < c.PARTITION_FRAC_THRESH     \
        or right_frac   < c.PARTITION_FRAC_THRESH: 

        return None

    left_fit,  left_fit_type  = make_fit(left_partition)
    right_fit, right_fit_type = make_fit(right_partition)
    return information_gain, [left_fit, right_fit], [left_fit_type, right_fit_type], \
        [left_entropy, right_entropy], [left_partition, right_partition]

def _make_partition(data, partition_data, orig_entropy):
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

    max_information_gain = None
    best_fit             = None
    best_fit_type        = None
    best_entropy         = None
    best_partition       = None
    best_partition_val   = None
    
    for partition_val in potential_partition_vals:
        partition_result = _partition(data, orig_entropy, partition_data, partition_val)

        if partition_result is not None:
            information_gain, fit, fit_type, entropy, partition = partition_result
            if max_information_gain is None or information_gain > max_information_gain:
                max_information_gain = information_gain
                
                best_fit        = fit
                best_fit_type   = fit_type
                best_entropy    = entropy
                best_partition  = partition
                best_partition_val = partition_val
                
    return best_fit, best_fit_type, best_entropy, best_partition, best_partition_val

def make_partitions(data, partition_data):
    max_partitions       = 5
    fits       = []
    fit_types  = []
    partition_vals = []
    partitions     = [data]
    entropies      = [_entropy(data)]
        
    for _ in range(max_partitions):
        to_partition_ind = np.argmax(entropies)
        subdata           = partitions[to_partition_ind]
        partition_subdata = partition_data[subdata.index]

        fit, fit_type, entropy, partition, partition_val = \
            _make_partition(subdata, partition_subdata, entropies[to_partition_ind])
        if fit is not None:
            fits = fits[:to_partition_ind] + fit + fits[to_partition_ind+1:]
            fit_types = fit_types[:to_partition_ind] + fit_type + fit_types[to_partition_ind+1:]
            entropies = entropies[:to_partition_ind] + entropy + entropies[to_partition_ind+1:]
            partition_vals.insert(to_partition_ind, partition_val)
            partitions = partitions[:to_partition_ind] + partition + partitions[to_partition_ind+1:]
        else: break
    return fits, fit_types, partition_vals, partitions