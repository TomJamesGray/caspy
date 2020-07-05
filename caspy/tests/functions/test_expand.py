from caspy.tests.test_symbolic import latex_eval


def test_square_expansion():
    assert latex_eval("expand((x+1)^2)") == "x^{2}+2\\cdotx+1"
