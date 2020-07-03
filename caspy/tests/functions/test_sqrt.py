from caspy.tests.test_symbolic import p, latex_eval
from caspy.numeric.fraction import Fraction
from hypothesis import given, settings
import hypothesis.strategies as st


@given(st.integers(min_value=-1000,max_value=1000))
def test_sqrt_of_square_num(x):
    assert latex_eval("sqrt({})".format(x**2)) == str(x)
