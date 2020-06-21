from caspy.parsing import parser
from caspy.printing.latex_numeric import latex_numeric_str

p = parser.Parser(output="ASCII")


def latex_eval(x):
    return latex_numeric_str(p.parse(x)).replace(" ", "")


def test_numeric_add():
    assert latex_eval("2+2") == "4"


def test_x_y_add():
    assert latex_eval("2+x+y") == "2+x+y"


def test_x_x_add():
    assert latex_eval("x+x") == "2\\cdotx"


def test_x_sq():
    assert latex_eval("x^2") == "x^{2}"


def test_repeat_exp():
    assert latex_eval("2^(3^4)") == "2^{3^{4}}"


def test_polyn():
    assert latex_eval("x^2+x") == "x^{2}+x"