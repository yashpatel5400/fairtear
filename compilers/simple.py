"""
__author__ = Yash Patel and Zachary Liu
__name__   = helper.py
__description__ = SimpleCompiler class that uses a maximum conditional depth of 1
and assumes only Gaussian distributed datasets
"""

import scipy.stats
import pandas as pd
import numpy as np

from compilers.helper import make_partition, make_fit

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
                fit, fit_type, _ = make_fit(df[partition_column])
                self.program[partition_column] = {
                    "fit" : fit,
                    "fit_type" : fit_type,
                    "partitions" : {}
                }
                completed.add(partition_column)

                for j, column in enumerate(df.columns[i+1:]):
                    fit, fit_type, partition = make_partition(df[column], 
                        df[partition_column], num_partitions=5)
                    
                    if fit is not None:
                        left_fit, right_fit = fit
                        left_fit_type, right_fit_type = fit_type
                        if partition not in self.program[partition_column]["partitions"]:
                            self.program[partition_column]["partitions"][partition] = {
                                "left" : {},
                                "right" : {}
                            }

                        self.program[partition_column]["partitions"][partition]["left"][column] = {
                            "fit" : left_fit,
                            "fit_type"   : left_fit_type,
                            "partitions" : {}
                        }
                        self.program[partition_column]["partitions"][partition]["right"][column] = {
                            "fit" : right_fit,
                            "fit_type"   : right_fit_type,
                            "partitions" : {}
                        }
                        completed.add(column)
        print("Compiled program tree!")
        
    def _recursive_frwrite(self, program, file_lines, num_tabs):
        tabs = "\t" * num_tabs
        for variable in program:
            file_lines.append("{}{} = {}{}\n".format(tabs, 
                variable, program[variable]["fit_type"], program[variable]["fit"]))
            if len(program[variable]["partitions"]) != 0:
                for partition in program[variable]["partitions"]:
                    partitions = program[variable]["partitions"][partition]
                    
                    file_lines.append("{}if {} <= {}:\n".format(tabs,  variable, partition))
                    self._recursive_frwrite(partitions["left"], file_lines, num_tabs=num_tabs+1)
                    file_lines.append("{}else:\n".format(tabs))
                    self._recursive_frwrite(partitions["right"],file_lines, num_tabs=num_tabs+1)

    def frwrite(self):
        print("Reading program tree into .fr format...")
        file_lines = ["def popModel():\n"]
        self._recursive_frwrite(self.program, file_lines, num_tabs=1)
        
        print("Writing final output...")
        with open(self.outfr, "w") as f:
            f.writelines(file_lines)
        print("Completed writing file to: {}".format(self.outfr))