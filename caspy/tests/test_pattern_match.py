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
    pmatch_res = pm.pmatch(pat, p.parse("{}*x".format(coeff)))
    assert pmatch_res == {"a": coeff}


@given(st.floats(min_value=-1000, max_value=1000).filter(lambda x: x != 0))
def test_pmatch_non_match(coeff):
    """Tests pattern matching with input a*x+y"""
    # Generate the pattern
    pat = pm.pat_construct("a*x", {"a": "const"})
    pmatch_res = pm.pmatch(pat, p.parse("{}*x+y".format(coeff)))
    assert pmatch_res == {}
