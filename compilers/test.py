"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Tests the models that are to be used for the final .fr
file generation
"""

from compilers.simple import SimpleCompiler
from compilers.recursive import RecursiveCompiler

def test_compilers(incsv, sensitive_attrs, qualified_attrs):
    """Tests the dataset compilers in the compilers/ directory pointed at by the
    input csv parameter provided.
    
    Parameters
    ----------
    dataset : str
        Filename of the csv where the input dataset is stored

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
    sc = SimpleCompiler(incsv=incsv, outfr="output/simple_ex.fr", 
        sensitive_attrs=sensitive_attrs, qualified_attrs=qualified_attrs)
    sc.compile()
    sc.frwrite()

    rc = RecursiveCompiler(incsv=incsv, outfr="output/recur_ex.fr", maxdepth=2,
        sensitive_attrs=sensitive_attrs, qualified_attrs=qualified_attrs)
    rc.compile()
    rc.frwrite()

if __name__ == "__main__":
    test_compilers("tests/ex.csv", [("ethnicity",">",10)],[])

    fr_input = """
    ethnicity = gaussian(0,100)
    colRank = gaussian(25,100)
    yExp = gaussian(10,25)
    if ethnicity > 10:
        colRank = colRank + 5
    sensitiveAttribute(ethnicity > 10)"""

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