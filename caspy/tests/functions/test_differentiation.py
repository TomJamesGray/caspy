import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from hypothesis import given


@given(st.floats(min_value=-1000, max_value=1000),
       st.floats(min_value=-1000, max_value=1000),
       st.floats(min_value=-1000, max_value=1000))
def test_diff_polyn(a, b, c):
    assert p.parse("diff({}*x^2+{}*x+{})".format(a, b, c)) == \
           p.parse("{}*x+{}".format(2 * a, b))


@given(st.floats(min_value=-1000, max_value=1000))
def test_diff_x_pow(n):
    assert p.parse("diff(x^({}))".format(n)) == p.parse("{}*x^({})".format(n, n-1))


def test_diff_sin():
    assert p.parse("diff(sin(x))") == p.parse("cos(x)")


def test_diff_cos():
    assert p.parse("diff(cos(x))") == p.parse("-sin(x)")


def test_diff_exp():
    assert p.parse("diff(e^(2*x))") == p.parse("2*e^(2*x)")


def test_diff_product():
    assert p.parse("diff(x*sin(x))") == p.parse("sin(x)+cos(x)*x")