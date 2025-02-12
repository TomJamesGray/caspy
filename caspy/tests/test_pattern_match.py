import caspy.pattern_match as pm
from hypothesis import given
import hypothesis.strategies as st
import caspy.parsing.parser

p = caspy.parsing.parser.Parser()


def test_x_once_coeff():
    """Tests pattern matching with input a*x"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("2*x"))
    assert pmatch_res == {"a": 2}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_x_coeff(coeff):
    """Tests pattern matching with input a*x"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("{}*x".format(coeff)))
    assert pmatch_res == {"a": coeff}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_pmatch_non_match(coeff):
    """Tests pattern matching with input a*x+y"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("{}*x+y".format(coeff)))
    assert pmatch_res == {}


def test_pmatch_polyn():
    pat = pm.pat_construct("a*x^2+b*x+c", {"a": "const", "b": "const", "c": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("2*x^2+3*x+1"))
    assert pmatch_res == {"a": 2, "b": 3, "c": 1}


def test_pmatch_polyn_one_zero():
    pat = pm.pat_construct("a*x^2+b*x+c", {"a": "const", "b": "const", "c": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("2*x^2+1"))
    assert pmatch_res == {"a": 2, "c": 1}


def test_pmatch_x_exp():
    pat = pm.pat_construct("x^a", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x^3"))
    assert pmatch_res == {"a": 3}


def test_pmatch_linear_sin_arg():
    pat = pm.pat_construct("a*sin(b*x+c)",
                           {"a": "const", "b": "const", "c": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("2*sin(3*x+10)"))
    assert pmatch_res == {"a": 2, "b": 3, "c": 10}


def test_recursion_return_part():
    pat = pm.pat_construct("b*x+c",
                           {"b": "const", "c": "const"})
    pmatch_res, pmatch_res_2 = pm.pmatch(pat, p.parse("x"))
    assert pmatch_res_2 == p.parse("x")


def test_pmatch_exp():
    pat = pm.pat_construct("e^a", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("e^3"))
    assert pmatch_res == {"a": 3}


def test_pmatch_exp_with_coeff():
    pat = pm.pat_construct("b*e^a", {"a": "const", "b": "const"})
    xyz = p.parse("2*e^3")
    pmatch_res, _ = pm.pmatch(pat, xyz)
    assert pmatch_res == {"a": 3, "b": 2}


def test_pmatch_exp_x_with_coeff():
    pat = pm.pat_construct("b*x^a", {"a": "const", "b": "const"})
    xyz = p.parse("10*x^3")
    pmatch_res, _ = pm.pmatch(pat, xyz)
    assert pmatch_res == {"a": 3, "b": 10}


def test_pmatch_exponentials():
    pat = pm.pat_construct("e^(b)", {"b": "rem"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("e^(x)"))
    assert pmatch_res == {"b": p.parse("x")}


def test_pmatch_exp_with_terms():
    pat = pm.pat_construct("x^(a*y)", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x^(3*y)"))
    assert pmatch_res == {"a": 3}


def test_pmatch_remaining():
    pat = pm.pat_construct("x^a + b", {"a": "const", "b": "rem"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x^3 + y*x"))
    assert pmatch_res == {"a": 3, "b": p.parse("y*x")}


def test_pmatch_fn_args():
    pat = pm.pat_construct("ln(a*x)", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("ln(3*x)"))
    assert pmatch_res == {"a": 3}


def test_pmatch_fn_args_non_match():
    pat = pm.pat_construct("ln(a*y)", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("ln(3*x)"))
    assert pmatch_res == {}


def test_pmatch_fn_args_rem():
    pat = pm.pat_construct("ln(a)", {"a": "rem"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("ln(x+y)"))
    assert pmatch_res == {"a": p.parse("x+y")}


def test_pmatch_fn_args_with_pow():
    pat = pm.pat_construct("ln(a*x)^2", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("ln(x)^2"))
    assert pmatch_res == {"a": 1}


def test_pmatch_fn_args_with_pow_non_match():
    pat = pm.pat_construct("ln(a*x)^2", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("ln(x)"))
    assert pmatch_res == {}


def test_pmatch_coeff():
    pat = pm.pat_construct("a*x", {"a": "coeff"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x^2*y*z"))
    assert pmatch_res == {"a": p.parse("x*y*z")}


def test_pmatch_coeff_with_const():
    pat = pm.pat_construct("a*b*y/z", {"a": "const", "b":"coeff"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("5*sin(x)*y/z"))
    assert pmatch_res == {"b": p.parse("sin(x)"), "a": 5}


def test_pmatch_coeff_sin():
    pat = pm.pat_construct("a*sin(b)", {"a": "coeff", "b": "rem"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x*sin(x^2)"))
    assert pmatch_res == {"a": p.parse("x"), "b": p.parse("x^2")}
