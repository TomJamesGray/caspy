from caspy.tests.test_symbolic import p,latex_eval
from caspy.numeric.fraction import Fraction
from hypothesis import given
import hypothesis.strategies as st

sin_pi_coeffs = [
    [Fraction(1, 2), "1"],
    [Fraction(1, 3), "sqrt(3)/2"],
    [Fraction(2, 3), "sqrt(3)/2"],
    [Fraction(1, 4), "sqrt(1/2)"],
    [Fraction(3, 4), "sqrt(1/2)"],
    [Fraction(1, 6), "1/2"],
    [Fraction(5, 6), "1/2"],
    [Fraction(1, 1), "0"],
    [Fraction(0, 1), "0"]
]

cos_pi_coeffs = [
    [Fraction(1, 2), "0"],
    [Fraction(1, 3), "1/2"],
    [Fraction(2, 3), "-1/2"],
    [Fraction(1, 4), "sqrt(2)/2"],
    [Fraction(3, 4), "-sqrt(2)/2"],
    [Fraction(1, 6), "sqrt(3)/2"],
    [Fraction(5, 6), "-sqrt(3)/2"],
    [Fraction(1, 1), "-1"],
    [Fraction(0, 1), "1"]
]


@given(st.integers(min_value=-1000, max_value=1000))
def test_sin_pis(x):
    assert latex_eval("sin({}*pi)".format(x)) == "0"


@given(st.integers(min_value=-1000, max_value=1000))
def test_cos_pis(x):
    if x % 2 == 0:
        assert latex_eval("cos({}*pi)".format(x)) == "1"
    else:
        assert latex_eval("cos({}*pi)".format(x)) == "-1"


@given(st.sampled_from(sin_pi_coeffs),st.integers(min_value=-1000,max_value=1000))
def test_sin_periodicity(pair,period):
    """Test sin has period 2pi"""
    assert latex_eval("sin({}*pi + {}*pi)".format(pair[0],2*period)) ==\
        latex_eval(pair[1])


@given(st.sampled_from(cos_pi_coeffs),st.integers(min_value=-1000,max_value=1000))
def test_cos_periodicity(pair,period):
    """Test cos has period 2pi"""
    assert latex_eval("cos({}*pi + {}*pi)".format(pair[0],2*period)) ==\
        latex_eval(pair[1])


@given(st.sampled_from(cos_pi_coeffs),st.integers(min_value=-1000,max_value=1000))
def test_cos_even(pair,period):
    """Test cos is an even function"""
    assert latex_eval("cos({}*pi + {}*pi)".format(pair[0], 2 * period)) == \
           latex_eval("cos(-({}*pi + {}*pi))".format(pair[0], 2 * period))
