from caspy.tests.test_symbolic import latex_eval,p


def test_square_expansion():
    assert p.parse("expand((x+1)^2)") == p.parse("1+x^2+2*x")


def test_brackets_expansion():
    assert p.parse("expand((y+2)*(y+3))") == p.parse("y^2+5*y+6")


def test_brackets_and_term_expansion():
    assert p.parse("expand(x*(x+2+y))") == p.parse("x^2+2*x+y*x")
