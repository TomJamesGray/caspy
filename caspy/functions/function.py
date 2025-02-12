import logging
import caspy.numeric.numeric as num
import caspy.numeric.symbol
import caspy.parsing
from caspy.numeric.fraction import Fraction
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg

    def eval(self):
        return num.Numeric(caspy.numeric.symbol.Symbol(self, Fraction(1, 1)), "sym_obj")

    def unicode_format(self):
        return self.ascii_format()


class Function1Arg(Function):
    def latex_format(self):
        return "{}({}) ".format(self.latex_fname, ln.latex_numeric_str(self.arg))

    def ascii_format(self):
        return "{}({})".format(self.fname, ln.latex_numeric_str(self.arg,"ascii"))

    def unicode_format(self):
        return "{}({})".format(self.fname, ln.latex_numeric_str(self.arg,"unicode"))

    def __deepcopy__(self, memodict={}):
        new = type(self)(self.arg)
        return new

    def __repr__(self):
        return "<Function {}, arg {}>".format(
            self.fname,ln.latex_numeric_str(self.arg)
        )
