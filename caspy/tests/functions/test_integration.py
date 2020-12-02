import hypothesis.strategies as st
from caspy.tests.test_symbolic import p,latex_eval
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


def test_int_sin():
    assert p.parse("integrate(sin(x))") == p.parse("-cos(x)")


def test_int_cos():
    assert p.parse("integrate(cos(x))") == p.parse("sin(x)")


def test_u_sub_int():
    assert p.parse("integrate(x*sin(x^2))") == p.parse("-cos(x^2)/2")


def test_u_sub_int_cos():
    assert p.parse("integrate(x*cos(x^2))") == p.parse("sin(x^2)/2")


def test_expand_then_int():
    assert p.parse("integrate((x+1)^2)") == p.parse("x^3/3+x^2+x")


def test_integrate_exp():
    assert p.parse("integrate(e^(x+5))") == p.parse("e^(x+5)")


def test_int_by_parts():
    assert p.parse("integrate(x*ln(x^2))") == p.parse("x^2 * ln(x^2)/2-x^2/2")


def test_expand_then_by_parts():
    assert p.parse("integrate((x+1)*sin(x))") == p.parse("integrate(expand((x+1)*sin(x)))")
