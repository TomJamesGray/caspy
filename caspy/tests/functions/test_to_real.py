import math
import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from hypothesis import given, settings
from datetime import timedelta


@given(st.floats(min_value=-100000, max_value=100000),
       st.floats(min_value=-100000, max_value=100000))
def test_to_real_addition(x, y):
    assert p.parse("re({}+{})".format(x, y)) == p.parse("{}".format(x + y))


@given(st.floats(min_value=-100000, max_value=100000),
       st.floats(min_value=-100000, max_value=100000))
def test_addition_of_real(x, y):
    assert p.parse("re({})+re({})".format(x, y)) == p.parse("{}".format(x + y))


@given(st.floats(min_value=-100000, max_value=100000))
def test_to_real_sin(x):
    assert p.parse("re(sin({}))".format(x)) == p.parse("{}".format(math.sin(x)))


@given(st.floats(min_value=-100000, max_value=100000))
def test_to_real_cos(x):
    assert p.parse("re(cos({}))".format(x)) == p.parse("{}".format(math.cos(x)))


# Default deadline is reached on travis, so increase it
@settings(deadline=timedelta(milliseconds=500))
@given(st.floats(min_value=-100000, max_value=100000))
def test_to_real_tan(x):
    assert p.parse("re(tan({}))".format(x)) == p.parse("{}".format(math.tan(x)))


@given(st.floats(min_value=0.0001, max_value=100000))
def test_to_real_log(x):
    assert p.parse("re(ln({}))".format(x)) == p.parse("{}".format(math.log(x)))
