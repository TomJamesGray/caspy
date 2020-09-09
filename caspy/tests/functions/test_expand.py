from caspy.tests.test_symbolic import latex_eval,p


def test_square_expansion():
    assert p.parse("expand((x+1)^2)") == p.parse("1+x^2+2*x")


def test_brackets_expansion():
    assert p.parse("expand((y+2)*(y+3))") == p.parse("y^2+5*y+6")


def test_brackets_and_term_expansion():
    assert p.parse("expand(x*(x+2+y))") == p.parse("x^2+2*x+y*x")


def test_expand_trig_sin():
    assert p.parse("expand_trig(sin(3*x))") == p.parse("sin(x)*cos(2*x)+2*cos(x)^2*sin(x)")


def test_expand_trig_cos():
    assert p.parse("expand_trig(cos(2*x))") == p.parse("cos(x)^2-sin(x)^2")
