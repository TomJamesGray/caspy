from caspy.parsing import parser as P
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction


class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg

    def __hash__(self):
        return hash("{}({})".format(self.fname,self.arg))


class Function1Arg(Function):
    def __init__(self):
        # TODO somehow use parser from main or otherwise to stop
        # re-initiallising parser which is probably quiet ineficient
        self.parser = P.Parser()
        self.evaled_set_points = []
        for (arg_val,f_val) in self.set_points:
            self.evaled_set_points.append([self.parser.parse(arg_val),
                                           self.parser.parse(f_val)])

    def eval(self):
        for i,pair in enumerate(self.evaled_set_points):
            if pair[0].simplify() == self.arg:
                return pair[1]

        return Numeric(Symbol(self,Fraction(1,1)),"sym_obj")
