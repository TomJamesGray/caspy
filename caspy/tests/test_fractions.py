from hypothesis import given
import hypothesis.strategies as st
from caspy.numeric.fraction import Fraction


@given(st.integers(min_value=-100000, max_value=100000),
       st.integers(min_value=-100000, max_value=100000).filter(lambda x: x != 0))
def test_fraction_simplification(a, b):
    """Tests that simplifying a fraction doesn't affect it's value"""
    frac = Fraction(a, b)
    assert frac.to_real() == a / b
