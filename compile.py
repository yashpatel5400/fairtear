"""
__author__ = Yash Patel and Zachary Liu
__name__   = compile.py
__description__ = Constructs the models that are to be used for the final .fr
file generation
"""

from compilers.simple import SimpleCompiler
from compilers.recursive import RecursiveCompiler

def test_compilers():
    # sc = SimpleCompiler(incsv="tests/ex.csv", outfr="output/ex.fr")
    # sc.compile()
    # sc.frwrite()

    rc = RecursiveCompiler(incsv="tests/ex.csv", outfr="output/ex.fr", maxdepth=2)
    rc.compile()
    rc.frwrite()

if __name__ == "__main__":
    test_compilers()

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