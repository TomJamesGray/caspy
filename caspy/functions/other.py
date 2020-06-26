import logging
from caspy.functions.function import Function1Arg
from caspy.printing import latex_numeric as ln
from caspy.numeric.symbol import Symbol
from caspy.numeric.numeric import Numeric
from caspy.numeric.fraction import Fraction

logger = logging.getLogger(__name__)


class Sqrt(Function1Arg):
    fname = "sqrt"
    set_points = []

    def __init__(self, x):
        self.arg = x
        # super().__init__()

    def latex_format(self):
        return "\\sqrt{{{}}}".format(ln.latex_numeric_str(self.arg))

    def eval(self):
        if self.arg.is_exclusive_numeric():
            logger.debug("Argument {} is just numeric".format(self.arg))
        else:
            logger.debug("Argument {} is not just numeric".format(self.arg))

        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")