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


def test_subs_linear_combination():
    tst_num = p.parse("sin(x)+sin(x)^2")
    replace = p.parse("sin(x)")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace, "u")
    assert replaced_obj == p.parse("u+u^2")


def test_subs_using_mults():
    tst_num = p.parse("1/x^4")
    replace = p.parse("x^2")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace, "u")
    assert replaced_obj == p.parse("1/u^2")
