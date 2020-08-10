from caspy.tests.test_symbolic import p


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