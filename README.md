# Caspy - A Python CAS [![Build Status](https://travis-ci.com/TomJamesGray/caspy.svg?token=yxBfcpPGRY4dC137hKoE&branch=master)](https://travis-ci.com/TomJamesGray/caspy) [![Coverage Status](https://coveralls.io/repos/github/TomJamesGray/caspy/badge.svg?branch=master&t=zN99sx)](https://coveralls.io/github/TomJamesGray/caspy?branch=master)

Caspy is a CAS that has been developed using Lark parser and Python. Some of the key feautures
are:

- Factorisation of univariate polynomials
- Integration and differentiation of symbollic variables
- Expansion of trigonometric expressions, eg expand sin(2x) as 2sin(x)cos(x)
- Expansion of expressions in brackets
- Automatic simplification of fractions and roots


## Dependencies
To just use the command line interface the only dependency is `lark-parser`, this can be installed with
```
pip install lark-parser
```

## Command line usage
To run Caspy you can either execute the `start-caspy.py` file with `python start-caspy.py` or execute the Caspy
module with `python -m caspy`. There are some command line arguments that can be passed to Caspy which determines how
verbose the output is and the type of the output Caspy will give these are
```
  -h, --help  show this help message and exit
  --timer     Time execution of statements
  --verbose   Enable verbose logging
  --debug     Enable more verbose logging for debugging purposes
  --ascii     Output string using ASCII characters
  --latex     Output representation of string in LaTeX form
  --unicode   Output string using Unicode characters

```

## Jupyter kernel
To use the Jupyter kernel interface the `jupyter` module must also be installed, this can be installed with
```
pip install jupyter
```
Then the jupyter kernel can be installed with 

```jupyter kernelspec install --user caspy```

## Functions implemented

Available functions in the system:

- `integrate(f(x),x)` : Integrate a function with respect to a variable x
- `diff(f(x),x)` : Differentiates a function with respect to a variable x
- `factor(f(x))` : Factorises a polynomial g(x) using Kronecker's algorithm
- `expand_trig(...)` : Expands a trigonometric expression, for instance
                      sin(2x) is expanded as 2sin(x)cos(x)
- `expand(...)` : Expands brackets in an expression 
- `re(...)` : Returns floating point answer where possible, for instance
            re(sqrt(2)) gives 1.4142...