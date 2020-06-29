from caspy.tests.test_symbolic import p,latex_eval
from hypothesis import given
import hypothesis.strategies as st


@given(st.integers(min_value=-1000, max_value=1000))
def test_sin_pis(x):
    assert latex_eval("sin({}*pi)".format(x)) == "0"


@given(st.integers(min_value=-1000, max_value=1000))
def test_cos_pis(x):
    if x % 2 == 0:
        assert latex_eval("cos({}*pi)".format(x)) == "1"
    else:
        assert latex_eval("cos({}*pi)".format(x)) == "-1"

