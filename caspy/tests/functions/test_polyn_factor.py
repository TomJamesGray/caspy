import hypothesis.strategies as st
from caspy.tests.test_symbolic import p
from caspy.functions.cas.kronecker_factorise import kronecker_int
from hypothesis import given, settings


def test_factor_one_var():
    assert p.parse("factor(x^2)") == p.parse("x^2")


def test_factor_eg_1():
    assert kronecker_int([1,0,0,0,-16]) == [[-1,-2],[-1,2],[1,0,4]]