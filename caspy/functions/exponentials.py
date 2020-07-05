import logging
import caspy.pattern_match
from caspy.functions.function import Function1Arg

logger = logging.getLogger(__name__)


class Ln(Function1Arg):
    fname = "ln"
    latex_fname = "\\ln"
    set_points = [
        ["e", "1"],
        ["e^2", "2"]
    ]

    def __init__(self, x):
        self.arg = x
        # super().__init__()

    def eval(self):
        pat = caspy.pattern_match.pat_construct("e^a", {"a": "const"})
        pmatch_res = caspy.pattern_match.pmatch(pat,self.arg)
        if pmatch_res != {}:
            logger.debug("Pmatch result {}".format(pmatch_res))

        return super().eval()
