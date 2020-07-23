import logging
import caspy.numeric.numeric as num
import caspy.numeric.symbol as sym
import caspy.parsing
from caspy.numeric.fraction import Fraction
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg

    def eval(self):
        return num.Numeric(sym.Symbol(self, Fraction(1, 1)), "sym_obj")


class Function1Arg(Function):
    def latex_format(self):
        return "{}({}) ".format(self.latex_fname, ln.latex_numeric_str(self.arg))

    def __deepcopy__(self, memodict={}):
        new = type(self)(self.arg)
        return new
