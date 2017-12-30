"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Tests the models that are to be used for the final .fr
file generation
"""

from compilers.simple import SimpleCompiler
from compilers.recursive import RecursiveCompiler

def test_compilers(incsv):
    """Tests the dataset compilers in the compilers/ directory pointed at by the
    input csv parameter provided.
    
    Parameters
    ----------
    dataset : str
        Filename of the csv where the input dataset is stored
    """
    sc = SimpleCompiler(incsv=incsv, outfr="output/simple_ex.fr")
    sc.compile()
    sc.frwrite()

    rc = RecursiveCompiler(incsv=incsv, outfr="output/recur_ex.fr", maxdepth=2)
    rc.compile()
    rc.frwrite()

if __name__ == "__main__":
    test_compilers("tests/ex.csv")

    fr_input = """
    ethnicity = gaussian(0,100)
    colRank = gaussian(25,100)
    yExp = gaussian(10,25)
    if ethnicity > 10:
        colRank = colRank + 5"""

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