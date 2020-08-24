import logging
from caspy.functions.function import Function1Arg

logger = logging.getLogger(__name__)


class ToReal(Function1Arg):
    fname = "re"
    latex_fname = "re"

    def __init__(self,x):
        self.arg = x

    def eval(self):
        val = self.arg.frac_eval()
        return val.to_real()
