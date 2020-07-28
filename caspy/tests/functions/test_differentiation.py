import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from hypothesis import given, settings


@given(st.floats(min_value=-1000, max_value=1000),
       st.floats(min_value=-1000, max_value=1000),
       st.floats(min_value=-1000, max_value=1000))
def test_diff_polyn(a, b, c):
    assert p.parse("diff({}*x^2+{}*x+{})".format(a, b, c)) == \
           p.parse("{}*x+{}".format(2 * a, b))


@given(st.floats(min_value=-1000, max_value=1000))
def test_diff_x_pow(n):
    assert p.parse("diff(x^({}))".format(n)) == p.parse("{}*x^({})".format(n, n-1))

