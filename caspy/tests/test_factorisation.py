from caspy.factorise import factoriseNum
from hypothesis import given
import hypothesis.strategies as st


def product(ns: [int]) -> int:
    if ns == []:
        return 0
    val = 1
    for n in ns:
        val = val * n
    return val


@given(st.integers(min_value=-100000, max_value=100000))
def tests_numeric_factorisation(x):
    assert product(factoriseNum(x)) == x
