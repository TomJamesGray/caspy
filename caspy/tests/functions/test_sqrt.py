from caspy.tests.test_symbolic import p, latex_eval
from caspy.numeric.fraction import Fraction
from hypothesis import given, settings
import hypothesis.strategies as st


@given(st.integers(min_value=0,max_value=1000))
def test_sqrt_of_square_num(x):
    assert latex_eval("sqrt({})".format(x**2)) == str(x)


@given(st.integers(min_value=0,max_value=1000))
def test_sqrt_of_square_num_2(x):
    assert latex_eval("sqrt({}^2)".format(x)) == str(x)
