from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg


class Ln(Function1Arg):
    fname = "ln"
    latex_fname = "\\ln"
    set_points = [
        ["e","1"],
        ["e^2","2"]
    ]

    def __init__(self,x):
        self.arg = x
        super().__init__()

    def eval(self):
        print(self.evaled_set_points)
        for i,pair in enumerate(self.evaled_set_points):
            if pair[0] == self.arg:
                return pair[1]

        return Numeric(Symbol(self,Fraction(1,1)),"sym_obj")
