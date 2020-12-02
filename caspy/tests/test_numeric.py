from caspy.tests.test_symbolic import p


def test_polyn_neq():
    assert p.parse("(x+1)") != p.parse("(x^4+x^3+x^2+x+1)")


def test_replace_numeric_with_var_divs():
    val = p.parse("(x^2+1)^(-2)")
    to_rep = p.parse("x^2+1")
    rep_with = p.parse("U1")
    assert val.try_replace_numeric_with_var(to_rep,rep_with) == p.parse("U1^(-2)")


def test_replace_numeric_with_var_mults():
    val = p.parse("(x^3+sin(x))^(2)")
    to_rep = p.parse("x^3+sin(x)")
    rep_with = p.parse("U1")
    assert val.try_replace_numeric_with_var(to_rep,rep_with) == p.parse("U1^(2)")


def test_repalce_numeric_with_var_func_arg():
    val = p.parse("x^2+1")
    to_rep = p.parse("x^2+1")
    rep_with = p.parse("U1")
    assert val.try_replace_numeric_with_var(to_rep, rep_with) == p.parse("U1")