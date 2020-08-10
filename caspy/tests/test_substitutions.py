import caspy.numeric.numeric
from caspy.tests.test_symbolic import p


def test_try_replace_numeric():
    tst_sym = p.parse("x^4").val[0]
    replace = p.parse("x^2")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_sym.try_replace_numeric_with_var(replace, var_obj)
    assert replaced_obj == p.parse("u^2")


def test_try_replace_numeric_with_func_xx():
    tst_sym = p.parse("x^4*sin(x^2)").val[0]
    replace = p.parse("x^2")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_sym.try_replace_numeric_with_var(replace,var_obj)
    assert replaced_obj == p.parse("sin(u)*u^2")


def test_try_replace_numeric_with_func_2():
    tst_sym = p.parse("sin(x^2)")
    replace = p.parse("x^2")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_sym.try_replace_numeric_with_var(replace, var_obj)
    assert replaced_obj == p.parse("sin(u)")


def test_try_replace_numeric_polyn():
    tst_num = p.parse("(x+1)^3")
    replace = p.parse("x+1")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace, var_obj)
    assert replaced_obj == p.parse("u^3")


def test_subs_linear_combination():
    tst_num = p.parse("sin(x)+sin(x)^2")
    replace = p.parse("sin(x)")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace, var_obj)
    assert replaced_obj == p.parse("u+u^2")


def test_subs_using_mults():
    tst_num = p.parse("1/x^4")
    replace = p.parse("x^2")
    var_obj = caspy.numeric.numeric.Numeric("u", "sym")
    replaced_obj = tst_num.try_replace_numeric_with_var(replace, var_obj)
    assert replaced_obj == p.parse("1/u^2")
