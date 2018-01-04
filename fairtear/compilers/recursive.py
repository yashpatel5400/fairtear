"""
__author__ = Yash Patel and Zachary Liu
__name__   = recursive.py
__description__ = RecursiveCompiler class, implemented recursively, where the maximum
recursion depth can be specified. This depth corresponds to the depth of the depth of
conditionals in the final .fr file
"""

import copy
import scipy.stats
import pandas as pd
import numpy as np

from compilers.helper import make_partitions, make_fit

class RecursiveCompiler:
    def __init__(self, x_csv, maxdepth, sensitive_attrs, qualified_attrs):
        """Recursive compiler, which assumes a maximum recursion depth as specified
        
        Parameters
        ----------
        x_csv : str
            Filename of the csv where the input dataset is stored
    
        maxdepth : int
            Integer of the maximum depth in the final output (i.e. of conditionals)

        sensitive_attrs : list of (str,str,int) tuples
            List of the names of attributes to be considered sensitive. Each attr has a
            "threshold" value, where we wish to mask whether the an individual's sensitive 
            attribute in relation to that threshold based on the 2nd param of the tuple. 
            The second param MUST either be ">" or "<", which respectively mean to hide 
            being below or exceeding a given threshold value. For example, if 
            the attribute is sex (step([0,1,.5],[1,2,.5])), the threshold can be set to 1
            w/ "<" to prevent us from knowing if (sex < 1)

        qualified_attrs : list of (str,str,int) tuples
            Same structure as sensitive_attrs. Used to qualify only particular members of the
            population, i.e. those satisfying the qualified conditionals. For example, if doing
            ("age",">",18), only those people of > 18 age will be considered in the population
        """
        self.x_csv = x_csv
        self.maxdepth = maxdepth
        self.sensitive_attrs = sensitive_attrs
        self.qualified_attrs = qualified_attrs
        self.program = {}

    def _clean_column(self, to_delete, program):
        """Given a list of partitions to be deleted from the program, cleans the 
        entries and deletes partitions if rendered empty
        
        Parameters
        ----------
        to_delete : list of str
            List of the partitions to delete from the program

        program : Dict (complex)
            Recursively defined structed (refer to _recursive_frwrite below for full
            documentation on structure)
        """
        partitions_to_delete = []
        for partition in program["partitions"]:
            for variable in to_delete:
                if variable in program["partitions"]:
                    del program["partitions"][partition][variable]
            if len(program["partitions"][partition]) == 0:
                partitions_to_delete.append(partition)
        
        for partition in partitions_to_delete:
            del program["partitions"][partition]

    def _recursive_compile(self, program, df, completed, partition_column, depth):
        """Recursive helper function to compile the program from the dataset. The
        parameters are used in the recursive calls. Returns the completed set, which
        contains the columns of the input dataframe that have been processed thus far
        
        Parameters
        ----------
        program : dict (complex)
            Recursively defined structed (refer to _recursive_frwrite below for full
            documentation on structure)
        
        df : Pandas dataframe
            Dataframe object of the input csv file

        completed : set of str
            Hashset of strings corresponding to the columns that have been processed
        
        partition_column : str
            Name of the column to be used for partitioning the dataframe/dataset

        depth : int
            Current depth of recursion (will be terminated if this value exceeds maxdepth)
        """
        if depth >= self.maxdepth:
            return completed

        for column in df.columns:
            if column in completed:
                continue

            fits, fit_types, partition_vals, partitions = make_partitions(df[column], 
                df[partition_column])

            if len(partition_vals) == 0:
                continue

            sub_completeds = []
            subprograms    = []
            for i in range(len(partition_vals)+1):
                if i == 0:
                    partition_range = (float("-inf"),partition_vals[i])
                elif i == len(partition_vals):
                    partition_range = (partition_vals[i-1],float("inf"))
                else:
                    partition_range = (partition_vals[i-1],partition_vals[i])
                
                fit = fits[i]
                fit_type = fit_types[i]
                partition = partitions[i]

                if partition_range not in program["partitions"]:
                    program["partitions"][partition_range] = {}

                program["partitions"][partition_range][column] = {
                    "fit"        : fit,
                    "fit_type"   : fit_type,
                    "partitions" : {}
                }

                subprogram = program["partitions"][partition_range][column]
                completed.add(column)

                if (depth + 1) < self.maxdepth:
                    sub_completed = self._recursive_compile(subprogram, df.loc[partition.index], 
                        copy.deepcopy(completed), column, depth+1)
                    sub_completeds.append(sub_completed)
                    subprograms.append(subprogram)
                    
            # have to delete those variables that were only partitioned on one of the
            # two sides (i.e. well partitioned on one side but not other)
            for i, subprogram in enumerate(subprograms):
                # have to ensure that each variable in the subcompleted is in ALL others
                self._clean_column(sub_completeds[i] - set.intersection(
                    *(sub_completeds[:i] + sub_completeds[i+1:])), subprogram)

            # add only those that are were completed on both sides to the completed set
            intersection = set()
            if len(sub_completeds) > 0:
                intersection = set.intersection(*sub_completeds)
            completed = completed.union(intersection)

        return completed

    def compile(self):
        """Compiles the csv dataset file into an internal "program" structure that is to
        be outputted as an .fr file. Mutates the self.program attribute
        
        Parameters
        ----------
        None
        """
        df = pd.read_csv(self.x_csv)
        completed = set()

        for i, partition_column in enumerate(df.columns):
            if partition_column in completed:
                continue

            print("Running partitioning on: {}...".format(partition_column))
            fit, fit_type, _ = make_fit(df[partition_column])
            self.program[partition_column] = {
                "fit" : fit,
                "fit_type" : fit_type,
                "partitions" : {}
            }

            completed.add(partition_column)
            completed = self._recursive_compile(self.program[partition_column], 
                df, completed, partition_column, depth=0)
            
        print("Compiled program tree!")
        
    def _recursive_frwrite(self, program, file_lines, num_tabs):
        """Helper function that recursively compiles the selfprogram attribute into
        a string to be written out to the .fr destination
        
        Parameters
        ----------
        program : Dict (complex)
            Recursively defined structed, that abides by the form:

            {
                "fit" : FitFunction(),
                "fit_type" : FitType,
                "partitions" : {
                    Float : subprogram,
                    Float : subprogram,
                    ...
                    Float : subprogram
                }
            }

            Where the FitFunction() is some set of parameters used to defined a probability
            distribution (i.e. mean/std), FitType is type of fit used (i.e. "gaussian"),
            and partitions are any values used as partitions for other variables. The
            subprogram values assigned to partition keys are themselves this structure

        file_lines : list of str
            List of string that contain the fr-compiled strings to be outputted

        num_tabs : int
            Current level of tabbing in the .fr file
        """
        tabs = "\t" * num_tabs
        for variable in program:
            file_lines.append("{}{} = {}{}\n".format(tabs, 
                variable, program[variable]["fit_type"], program[variable]["fit"]))
            if len(program[variable]["partitions"]) != 0:
                partition_ranges = sorted(program[variable]["partitions"])
                for i, partition_range in enumerate(partition_ranges):
                    lower_bound, upper_bound = partition_range

                    if   i == 0: conditional = "if"
                    else: conditional = "elif"

                    if lower_bound == float("-inf"):
                        lower_bound_str = ""
                    else: lower_bound_str = "{} < ".format(str(lower_bound))

                    if upper_bound == float("inf"):
                        upper_bound_str = ""
                    else: upper_bound_str = " <= {}".format(str(upper_bound))

                    file_lines.append("{}{} {}{}{}:\n".format(tabs, conditional, 
                        lower_bound_str, variable, upper_bound_str))
                    
                    subprogram = program[variable]["partitions"][partition_range]
                    self._recursive_frwrite(subprogram, file_lines, num_tabs=num_tabs+1)

    def frwrite(self, file):
        """Writes the self.program attribute into the standard .fr file format to
        be interpreted by FairSquare, saved to the outfr file destination
        
        Parameters
        ----------
        file : File pointer object
            File pointer to where the contents are to be written to disk
        """
        print("Reading program tree into .fr format...")
        file_lines = ["def popModel():\n"]
        self._recursive_frwrite(self.program, file_lines, num_tabs=1)
        
        for sensitive_attr, comp, thresh in self.sensitive_attrs:
            file_lines.append("\tsensitiveAttribute({} {} {})\n".format(
                sensitive_attr, comp, thresh))
        for qualified_attr, comp, thresh in self.qualified_attrs:
            file_lines.append("\tqualified({} {} {})\n".format(
                qualified_attr, comp, thresh))

        file_lines.append("\n")
        print("Writing final output...")
        file.writelines(file_lines)
        file.close()
        print("Completed writing file!")