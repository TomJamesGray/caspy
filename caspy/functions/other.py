import logging
from caspy.functions.function import Function1Arg
from caspy.printing import latex_numeric as ln
from caspy.numeric.symbol import Symbol
from caspy.numeric.numeric import Numeric
from caspy.numeric.fraction import Fraction
from caspy.factorise import factoriseNum

logger = logging.getLogger(__name__)


class Sqrt(Function1Arg):
    fname = "sqrt"

    def __init__(self, x):
        self.arg = x

    def latex_format(self):
        return "\\sqrt{{{}}}".format(ln.latex_numeric_str(self.arg))

    def eval(self):
        if self.arg.is_exclusive_numeric():
            logger.debug("Attempting to simplify {} for sqrt".format(self.arg))
            if len(self.arg.val) > 1:
                logger.warning("Argument {} is exclusively numeric but"
                               "contains more than 1 symbol. Not trying"
                               "to simplify").format(self.arg)
            else:
                # Attempt to simplify
                sym = self.arg.val[0]
                # Removing this breaks sqrt(1/4) for example?!?!
                sym.simplify()
                sym_val = sym.sym_real_eval()
                logger.debug("Simplifying argument {}".format(sym_val))

        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")
