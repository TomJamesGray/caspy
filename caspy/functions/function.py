import logging
import caspy.numeric.numeric as num
import caspy.numeric.symbol as sym
from caspy.parsing import parser as P
from caspy.numeric.fraction import Fraction
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg


class Function1Arg(Function):
    def __init__(self):
        # TODO somehow use parser from main or otherwise to stop
        # re-initialising parser which is probably quiet ineficient

        # Disable logging while initialising function
        previous_level = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.parser = P.Parser()
        self.evaled_set_points = []
        for (arg_val,f_val) in self.set_points:
            self.evaled_set_points.append([self.parser.parse(arg_val),
                                           self.parser.parse(f_val)])
        logging.disable(previous_level)

    def eval(self):
        for i,pair in enumerate(self.evaled_set_points):
            if pair[0] == self.arg:
                return pair[1]

        return num.Numeric(sym.Symbol(self,Fraction(1,1)),"sym_obj")

    def latex_format(self):
        return "{}({}) ".format(self.latex_fname, ln.latex_numeric_str(self.arg))
