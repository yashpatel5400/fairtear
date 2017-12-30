"""
__author__ = Yash Patel and Zachary Liu
__name__   = helper.py
__description__ = SimpleCompiler class that uses a maximum conditional depth of 1
and assumes only Gaussian distributed datasets
"""

import scipy.stats
import pandas as pd
import numpy as np

from compilers.helper import make_partition

class SimpleCompiler:
    """Simplest compiler, which assumes a maximum recursion depth of 1 and that all
    the data are Gaussian distributed. 
    """

    def __init__(self, incsv, outfr):
        self.incsv = incsv
        self.outfr = outfr
        self.program = {}

    def compile(self):
        completed = set()

        df = pd.read_csv(self.incsv)
        for i, partition_column in enumerate(df.columns):
            print("Running partitioning on: {}...".format(partition_column))
            if partition_column not in completed:
                mu, std = scipy.stats.norm.fit(df[partition_column])
                self.program[partition_column] = {
                    "fit" : (mu, std),
                    "partitions" : {}
                }
                completed.add(partition_column)

                for j, column in enumerate(df.columns[i+1:]):
                    fit, partition = make_partition(df[column], 
                        df[partition_column], num_partitions=5)
                    
                    if fit is not None:
                        left_fit, right_fit = fit
                        if partition not in self.program[partition_column]["partitions"]:
                            self.program[partition_column]["partitions"][partition] = {
                                "left" : {},
                                "right" : {}
                            }

                        self.program[partition_column]["partitions"][partition]["left"][column] = {
                            "fit" : left_fit,
                            "partitions" : {}
                        }
                        self.program[partition_column]["partitions"][partition]["right"][column] = {
                            "fit" : right_fit,
                            "partitions" : {}
                        }
                        completed.add(column)
        print("Compiled program tree!")
        
    def frwrite(self):
        file_lines = ["def popModel():\n"]
        print("Reading program tree into .fr format...")
        for variable in self.program:
            file_lines.append("\t{} = gaussian{}\n".format(variable, self.program[variable]["fit"]))
            if len(self.program[variable]["partitions"]) != 0:
                for partition in self.program[variable]["partitions"]:
                    partitions = self.program[variable]["partitions"][partition]
                    
                    file_lines.append("\tif {} <= {}:\n".format(variable, partition))
                    for dependent in partitions["left"]:
                        file_lines.append("\t\t{} = gaussian{}\n".format(
                            dependent, partitions["left"][dependent]["fit"]))
                    file_lines.append("\telse:\n")
                    for dependent in partitions["right"]:
                        file_lines.append("\t\t{} = gaussian{}\n".format(
                            dependent, partitions["right"][dependent]["fit"]))
        
        print("Writing final output...")
        with open(self.outfr, "w") as f:
            f.writelines(file_lines)
        print("Completed writing file to: {}".format(self.outfr))