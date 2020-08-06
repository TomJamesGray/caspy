from caspy.tests.test_symbolic import p


def test_try_replace_numeric():
    tst_sym = p.parse("x^4").val[0]
    replace = p.parse("x^2")
    replaced_obj = tst_sym.try_replace_numeric_with_var(replace,"u")
    assert replaced_obj == p.parse("u^2")


def test_try_replace_numeric_with_func():
    tst_sym = p.parse("x^4*sin(x^2)").val[0]
    replace = p.parse("x^2")
    replaced_obj = tst_sym.try_replace_numeric_with_var(replace,"u")
    assert replaced_obj == p.parse("sin(u)*u^2")


def test_try_replace_numeric_polyn():
    tst_num = p.parse("(x+1)^3")
    replace = p.parse("x+1")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace,"u")
    assert replaced_obj == p.parse("u^3")


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
