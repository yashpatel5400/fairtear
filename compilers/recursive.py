"""
__author__ = Yash Patel and Zachary Liu
__name__   = helper.py
__description__ = RecursiveCompiler class, implemented recursively, where the maximum
recursion depth can be specified. This depth corresponds to the depth of the depth of
conditionals in the final .fr file
"""

import copy
import scipy.stats
import pandas as pd
import numpy as np

from compilers.helper import make_partition

class RecursiveCompiler:
    """Recursive compiler, which assumes a maximum recursion depth as specified and that all
    the data are Gaussian distributed. 
    """
    def __init__(self, incsv, outfr, maxdepth=2):
        self.incsv = incsv
        self.outfr = outfr
        self.maxdepth = maxdepth
        self.program = {}

    def _clean_column(self, to_delete, column):
        partitions_to_delete = []
        for partition in column["partitions"]:
            for variable in to_delete:
                del column["partitions"][partition]["left"][variable]
                del column["partitions"][partition]["right"][variable]
            
            if len(column["partitions"][partition]["left"]) == 0:
                partitions_to_delete.append(partition)
        
        for partition in partitions_to_delete:
            del column["partitions"][partition]

    def _recursive_compile(self, program, df, completed, partition_column, depth):
        if depth >= self.maxdepth:
            return completed

        for column in df.columns:
            if column in completed:
                continue

            fit, partition = make_partition(df[column], 
                df[partition_column], num_partitions=5)
            if fit is not None:
                left_fit, right_fit = fit
                if partition not in program["partitions"]:
                    program["partitions"][partition] = {
                        "left" : {},
                        "right" : {}
                    }

                program["partitions"][partition]["left"][column] = {
                    "fit" : left_fit,
                    "partitions" : {}
                }
                program["partitions"][partition]["right"][column] = {
                    "fit" : right_fit,
                    "partitions" : {}
                }
                
                completed.add(column)
                left_subprogram  = program["partitions"][partition]["left"][column]
                right_subprogram = program["partitions"][partition]["right"][column]
                
                left_partition  = df[df[partition_column] <= partition]
                right_partition = df[df[partition_column] > partition]

                if (depth + 1) < self.maxdepth:
                    left_completed  = self._recursive_compile(left_subprogram, left_partition, 
                        copy.deepcopy(completed), column, depth+1)
                    right_completed = self._recursive_compile(right_subprogram, right_partition, 
                        copy.deepcopy(completed), column, depth+1)

                    # have to delete those variables that were only partitioned on one of the
                    # two sides (i.e. well partitioned on one side but not other)
                    self._clean_column(left_completed - right_completed, left_subprogram)
                    self._clean_column(right_completed - left_completed, right_subprogram)

                    # add only those that are were completed on both sides to the completed set
                    completed = completed.union(left_completed.intersection(right_completed))
        return completed

    def compile(self):
        df = pd.read_csv(self.incsv)
        completed = set()

        for i, partition_column in enumerate(df.columns):
            if partition_column in completed:
                continue

            print("Running partitioning on: {}...".format(partition_column))
            mu, std = scipy.stats.norm.fit(df[partition_column])
            self.program[partition_column] = {
                "fit" : (mu, std),
                "partitions" : {}
            }

            completed.add(partition_column)
            completed = self._recursive_compile(self.program[partition_column], 
                df, completed, partition_column, depth=0)
            print("===============================================")
            
        print("Compiled program tree!")
        
    def _recursive_frwrite(self, program, file_lines, num_tabs):
        tabs = "\t" * num_tabs
        for variable in program:
            file_lines.append("{}{} = gaussian{}\n".format(tabs, 
                variable, program[variable]["fit"]))
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