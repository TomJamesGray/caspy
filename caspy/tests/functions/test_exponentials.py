import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from hypothesis import given, settings


@given(st.floats(min_value=-1000,max_value=1000))
def test_log_of_exp_pow(x):
    assert p.parse("ln(e^({}))".format(x)) == p.parse(str(x))
