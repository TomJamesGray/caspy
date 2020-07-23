import caspy.pattern_match as pm
from hypothesis import given
import hypothesis.strategies as st
import caspy.parsing.parser

p = caspy.parsing.parser.Parser()


def test_x_once_coeff():
    """Tests pattern matching with input a*x"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("2*x"))
    assert pmatch_res == {"a": 2}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_x_coeff(coeff):
    """Tests pattern matching with input a*x"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    print("Pattern exlcusive numeric? {}".format(pat.is_exclusive_numeric()))
    pmatch_res,_ = pm.pmatch(pat, p.parse("{}*x".format(coeff)))
    assert pmatch_res == {"a": coeff}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_pmatch_non_match(coeff):
    """Tests pattern matching with input a*x+y"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("{}*x+y".format(coeff)))
    assert pmatch_res == {}


def test_pmatch_polyn():
    pat = pm.pat_construct("a*x^2+b*x+c", {"a": "const","b": "const","c": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("2*x^2+3*x+1"))
    assert pmatch_res == {"a":2,"b":3,"c":1}


def test_pmatch_polyn_one_zero():
    pat = pm.pat_construct("a*x^2+b*x+c", {"a": "const", "b": "const", "c": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("2*x^2+1"))
    assert pmatch_res == {"a": 2,"c": 1}


def test_pmatch_x_exp():
    pat = pm.pat_construct("x^a", {"a": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("x^3"))
    assert pmatch_res == {"a": 3}


def test_pmatch_exp():
    pat = pm.pat_construct("e^a", {"a": "const"})
    pmatch_res,_ = pm.pmatch(pat, p.parse("e^3"))
    assert pmatch_res == {"a":3}


def test_pmatch_exp_with_coeff():
    pat = pm.pat_construct("b*e^a", {"a": "const","b":"const"})
    xyz = p.parse("2*e^3")
    pmatch_res,_ = pm.pmatch(pat, xyz)
    assert pmatch_res == {"a":3,"b":2}


def test_pmatch_exp_x_with_coeff():
    pat = pm.pat_construct("b*x^a", {"a": "const","b":"const"})
    xyz = p.parse("10*x^3")
    pmatch_res,_ = pm.pmatch(pat, xyz)
    assert pmatch_res == {"a":3,"b":10}


def test_pmatch_exp_with_terms():
    pat = pm.pat_construct("x^(a*y)", {"a": "const"})
    pmatch_res, _ = pm.pmatch(pat, p.parse("x^(3*y)"))
    assert pmatch_res == {"a": 3}
