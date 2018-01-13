"""
__author__ = Yash Patel and Zachary Liu
__name__   = simple.py
__description__ = SimpleCompiler class that uses a maximum conditional depth of 1
and assumes only Gaussian distributed datasets
"""

import scipy.stats
import pandas as pd
import numpy as np

from fairtear.compilers.helper import make_partitions, make_fit

class SimpleCompiler:
    def __init__(self, df, outfr, sensitive_attrs, qualified_attrs):
        """Simplest compiler, which assumes a maximum recursion depth of 1
        
        Parameters
        ----------
        df : DataFrame
            Pandas DataFrame containing the input dataset

        outfr : str
            Filename where the output (.fr file) is to be stored

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
        self.df = df
        self.outfr = outfr
        self.sensitive_attrs = sensitive_attrs
        self.qualified_attrs = qualified_attrs
        self.program = {}

    def compile(self):
        """Compiles the dataset into an internal "program" structure that is to
        be outputted as an .fr file. Mutates the self.program attribute
        
        Parameters
        ----------
        None
        """
        completed = set()

        for i, partition_column in enumerate(self.df.columns):
            print("Running partitioning on: {}...".format(partition_column))
            if partition_column not in completed:
                fit, fit_type, _ = make_fit(self.df[partition_column])
                self.program[partition_column] = {
                    "fit" : fit,
                    "fit_type" : fit_type,
                    "partitions" : {}
                }
                completed.add(partition_column)

                for j, column in enumerate(self.df.columns[i+1:]):
                    fit, fit_type, partition = make_partitions(self.df[column], 
                        self.df[partition_column])
                    
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
                for partition in program[variable]["partitions"]:
                    partitions = program[variable]["partitions"][partition]
                    
                    file_lines.append("{}if {} <= {}:\n".format(tabs,  variable, partition))
                    self._recursive_frwrite(partitions["left"], file_lines, num_tabs=num_tabs+1)
                    file_lines.append("{}else:\n".format(tabs))
                    self._recursive_frwrite(partitions["right"],file_lines, num_tabs=num_tabs+1)

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
        print("Completed writing file to: {}".format(self.outfr))