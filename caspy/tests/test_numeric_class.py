from caspy.tests.test_symbolic import p


def test_numeric_equality():
    assert p.parse("sqrt(3)/3") == p.parse("1/sqrt(3)")
