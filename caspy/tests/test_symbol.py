from caspy.tests.test_symbolic import p
from lark.exceptions import VisitError


def test_get_variables_in_func():
    num = p.parse("x*sin(u)")
    assert num.get_variables_in() == {"x", "u"}


def test_get_variables_in_polyn():
    num = p.parse("(x+y)^2")
    assert num.get_variables_in() == {"x", "y"}


def test_get_variables_in_exp():
    num = p.parse("2^a")
    assert num.get_variables_in() == {"a"}


def test_get_variables_in_linear():
    num = p.parse("a+b+x*y")
    assert num.get_variables_in() == {"a", "b", "x", "y"}


def test_is_zero():
    num = p.parse("1-1")
    assert num.is_zero()


def test_div_by_zero():
    try:
        _ = p.parse("2/0")
    except (ZeroDivisionError, VisitError):
        # Program fails correctly
        assert True
    else:
        assert False
