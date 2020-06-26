from caspy.functions.function import Function1Arg
from caspy.printing import latex_numeric as ln


class Sqrt(Function1Arg):
    fname = "sqrt"
    set_points = []

    def __init__(self, x):
        self.arg = x
        super().__init__()

    def latex_format(self):
        return "\\sqrt{{{}}}".format(ln.latex_numeric_str(self.arg))
