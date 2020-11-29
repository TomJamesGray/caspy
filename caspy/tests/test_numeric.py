from caspy.tests.test_symbolic import p


def test_polyn_neq():
    assert p.parse("(x+1)") != p.parse("(x^4+x^3+x^2+x+1)")
