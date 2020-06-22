from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function,Function1Arg


class Ln(Function,Function1Arg):
    fname = "ln"

    def __init__(self,x):
        self.arg = x

    def eval(self):
        if self.arg == Numeric("e","sym"):
            return Numeric(1,"number")
        else:
            # return Numeric(Symbol(self,Fraction(1,1)),"sym_obj")
            return Numeric(Symbol(self,Fraction(1,1)),"sym_obj")
