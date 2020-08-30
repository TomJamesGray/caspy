import logging
import caspy.numeric.numeric
from caspy.functions.function import Function1Arg

logger = logging.getLogger(__name__)


class ToReal(Function1Arg):
    fname = "re"
    latex_fname = "re"

    def __init__(self, x, float_rep=False):
        self.arg = x
        self.float_rep = float_rep

    def eval(self):
        val = self.arg.frac_eval()
        if self.float_rep:
            return val.to_real()
        else:
            return caspy.numeric.numeric.Numeric(val, "number")
