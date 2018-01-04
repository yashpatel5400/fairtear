# Tests
__DEPRECATED__ : Refer now to the data/ directory for tests

Where all the test .csv files are saved. These are used to represent trials where the population model is internally known to to see whether the correct .fr files can be created as a result.

## simple.csv
Distribution (from ex.fr):
```
ethnicity = gaussian(0,100)
colRank = gaussian(25,100)
yExp = gaussian(10,25)
if ethnicity > 10:
    colRank = colRank + 5
sensitiveAttribute(ethnicity > 10)
```

## multi.csv
Distribution (from ex.fr):
```
sex = gaussian(1,1)
if sex < 1:
    capital_gain = gaussian(568.4105, 24248365.5428)
    if capital_gain < 7298.0000:
        age = gaussian(38.4208, 184.9151)
        education_num = gaussian(10.0827, 6.5096)
    else:
        age = gaussian(38.8125, 193.4918)
        education_num = gaussian(10.1041, 6.1522)
else:
    capital_gain = gaussian(1329.3700, 69327473.1006)
    if capital_gain < 5178.0000:
        age = gaussian(38.6361, 187.2435)
        education_num = gaussian(10.0817, 6.4841)
    else:
        age = gaussian(38.2668, 187.2747)
        education_num = gaussian(10.0974, 7.1793)
sensitiveAttribute(sex < 1)
```