# FairTear
<img src="fairtear/static/img/logo.png" alt="logo" width="200px"/>

Tool to tear apart algorithm-dataset pairs to determine whether they are fair or not. FairTear heavily relies on [FairSquare](https://github.com/sedrews/fairsquare), and this effort would not have been possible without the generous open-sourcing of its code. The tool primarily serves as an application layer abstraction on the FairSquare back-end, taking as input the dataset on which a classifier was trained on (separated into the features and target csv files) and the classifier itself (saved as a binary pickle file). Details on use and supported classifiers is given below.

To read more in-depth on the math and underlying principles at play in FairTear, please read: **[Automated Probabilistic Analysis on Dataset Models](FairTear.pdf)** by
[Yash Patel](https://github.com/yashpatel5400) and
[Zachary Liu](https://github.com/zacharyliu).

## Setup

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

FairSquare is written in Python 3 and uses Pipenv for dependency management. It has been tested on Linux and Mac.

First, clone this repository and its FairSquare submodule:

```
git clone git@github.com:yashpatel5400/fairtear.git
cd fairtear
git submodule init
```

If Pipenv is not yet installed on your system, it can be installed with this command:

```
pip install pipenv
```

Finally, install the Python dependencies (this may take a while if you do not have scipy or other large dependencies already built):

```
pipenv install
```

### Optional: Redlog

By default, FairTear is configured to launch FairSquare using a built-in DNF-based quantifier elimination implemented with z3, and no additional dependencies are needed. Alternatively, FairSquare can also be launched using [redlog](http://www.redlog.eu/get-redlog/) for quantifier elimination. If desired, this must be downloaded separately. 

FairSquare expects the downloaded files to be placed in its `src/tools/` directory (specifically, it runs `src/tools/reduce`, which relies on the existence of `src/tools/reduce.img`). To set this up:

```
cd fairtear/external/fairsquare/src
mkdir tools
cd tools
wget http://www.redlog.eu/get-redlog/dist/x86_64-unknown-debian7.9_svn3258.tgz
tar -xvzf x86_64-unknown-debian7.9_svn3258.tgz
```

## Usage

Once the dependencies are installed, the app can be run in one of two ways:
- Web app
- Back-end analysis

### Web App
To run the web app, simply run the `run.py` file within Pipenv using:

```pipenv run python run.py```

This will launch the server at the URL `http://localhost:8080` by default.

### Back-end Analysis

Run the standalone compiler with:

```pipenv run python compile.py```

## Contributors

* [Yash Patel](https://github.com/yashpatel5400)
* [Zachary Liu](https://github.com/zacharyliu)
