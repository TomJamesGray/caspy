import caspy.pattern_match as pm
from hypothesis import given
import hypothesis.strategies as st
import caspy.parsing.parser

p = caspy.parsing.parser.Parser()


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_x_coeff(coeff):
    """Tests pattern matching with input a*x"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    print("Pattern exlcusive numeric? {}".format(pat.is_exclusive_numeric()))
    pmatch_res = pm.pmatch(pat, p.parse("{}*x".format(coeff)))
    assert pmatch_res == {"a": coeff}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_pmatch_non_match(coeff):
    """Tests pattern matching with input a*x+y"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res = pm.pmatch(pat, p.parse("{}*x+y".format(coeff)))
    assert pmatch_res == {}


def test_pmatch_polyn():
    pat = pm.pat_construct("a*x^2+b*x+c", {"a": "const","b": "const","c": "const"})
    print("Pattern exlcusive numeric? {}".format(pat.is_exclusive_numeric()))
    xyz = p.parse("2*x^2+3*x+1")
    print("Other exlcusive numeric? {}".format(xyz.is_exclusive_numeric()))
    pmatch_res = pm.pmatch(pat, p.parse("2*x^2+3*x+1"))
    assert pmatch_res == {"a":2,"b":3,"c":1}


def test_pmatch_exp():
    pat = pm.pat_construct("e^a", {"a": "const"})
    print("Pattern exlcusive numeric? {}".format(pat.is_exclusive_numeric()))
    xyz = p.parse("e^3")
    print("Other exlcusive numeric? {}".format(xyz.is_exclusive_numeric()))
    pmatch_res = pm.pmatch(pat, p.parse("e^3"))
    assert pmatch_res == {}
