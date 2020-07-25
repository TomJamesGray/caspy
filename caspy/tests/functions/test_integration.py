import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from hypothesis import given, settings


def test_integrate_polyn():
    assert p.parse("integrate(2*x^2+x+2)") == p.parse("2*x^3/3+x^2/2+2*x")


@given(st.floats(min_value=-1000,max_value=1000))
def test_integrate_const(x):
    assert p.parse("integrate({})".format(x)) == p.parse("{}*x".format(x))


@given(st.floats(min_value=-1000,max_value=1000))
def test_integrate_const_wrt_y(x):
    assert p.parse("integrate({},y)".format(x)) == p.parse("{}*y".format(x))


def test_integrate_recip():
    assert p.parse("integrate(1/x)") == p.parse("ln(x)")
