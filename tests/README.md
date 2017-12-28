# Tests
Where all the test .csv files are saved. These are used to represent trials where the population model is internally known to to see whether the correct .fr files can be created as a result.

## basic.csv
Distribution (from ex.fr):
```
ethnicity = gaussian(0,100)
colRank = gaussian(25,100)
yExp = gaussian(10,25)
if ethnicity > 10:
    colRank = colRank + 5
sensitiveAttribute(ethnicity > 10)
```