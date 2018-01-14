# FairTear
<img src="fairtear/static/img/logo.png" alt="logo" width="200px"/>

Tool to tear apart algorithm-dataset pairs to determine whether they are fair or not. FairTear heavily relies on [FairSquare](https://github.com/sedrews/fairsquare), and this effort would not have been possible without the generous open-sourcing of its code. The tool primarily serves as an application layer abstraction on the FairSquare back-end, taking as input the dataset on which a classifier was trained on (separated into the features and target csv files) and the classifier itself (saved as a binary pickle file). Details on use and supported classifiers is given below.

To read more in-depth on the math and underlying principles at play in FairTear, please read: **Automated Probabilistic Analysis on Dataset Models** by
[Yash Patel](https://github.com/yashpatel5400) and
[Zachary Liu](https://github.com/zacharyliu).

## Installation

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

FairSquare runs (best) on Linux and uses Python 3. Note: By default, we assume you have pip3 mapped to the pip tool for Python 3. If it is simply pip (or something else), replace all instances of pip3 with your corresponding name.

### FairSquare
Since FairTear uses FairSquare as necessary dependency, the following steps must be completed to set up FairSquare (assuming you have not already cloned the repo):

```
git clone https://github.com/yashpatel5400/fairtear.git
cd fairtear/external
git clone https://github.com/yashpatel5400/fairsquare.git
```

**Important Note:** The FairSquare repo you clone _must_ be the forked one reference in the above instructions, **not** the original one developed under sedrews. This forked version makes a crucial change, without which FairTear cannot produce a final result.

From here, you must follow the [FairSquare](https://github.com/yashpatel5400/fairsquare) README guide for setting up FairSquare. For convenience, the steps are copied below (assuming you to still be in the fairtear/external directory):

Additionally, it uses the following dependencies:
- [z3](http://github.com/Z3Prover/z3):
```
git clone https://github.com/Z3Prover/z3.git
python3 --python scripts/mk_make.py
cd build
make
sudo make install
```

- [SciPy](http://scipy.org/) stack:
```pip3 install --user numpy scipy matplotlib ipython jupyter pandas sympy nose```

- python packages `codegen` and `asteval`(easily obtained using [pip3](http://pypi.python.org/pypi/pip3):
```pip3 install --user codegen asteval```

By default, FairSqaure uses [redlog](http://www.redlog.eu/get-redlog/) for quantifier elimination, which must be downloaded separately: FairSquare expects the downloaded files to be placed in `src/tools/` (specifically, it runs `src/tools/reduce`, which relies on the existence of `src/tools/reduce.img`). To set this up (assuming you're in the fairtear/external directory):

```
cd fairsquare/src
mkdir tools
cd tools
wget http://www.redlog.eu/get-redlog/dist/x86_64-unknown-debian7.9_svn3258.tgz
tar -xvzf x86_64-unknown-debian7.9_svn3258.tgz
```

Alternatively, FairSquare can use a DNF-based quantifier elimination implemented with z3 by using the `-z` flag when running the tool.

### FairTear
In addition to the dependencies required for FairSquare, there are some that must be installed for FairTear. To finish setting up, simply run:

```
pip3 install -r requirements.txt
```

## Running the tool

Once the dependencies are installed, the app can be run in one of two ways:
- Web app
- Back-end analysis

### Web App
To run the web app, simply run the `run.py` file using:

```python3 run.py```

This will open up the application on `localhost:8080` by default.

### Back-end Analysis

Run `compile.py`

## Contributors

* [Yash Patel](https://github.com/yashpatel5400)
* [Zachary Liu](https://github.com/zacharyliu)
