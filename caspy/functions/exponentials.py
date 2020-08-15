import logging
import caspy.pattern_match
import caspy.numeric.numeric
from caspy.functions.function import Function1Arg

logger = logging.getLogger(__name__)


class Ln(Function1Arg):
    fname = "ln"
    latex_fname = "\\ln"

    def __init__(self, x):
        self.arg = x
        # super().__init__()

    def eval(self):
        pat = caspy.pattern_match.pat_construct("e^a", {"a": "const"})
        pmatch_res, _ = caspy.pattern_match.pmatch(pat, self.arg)

        if pmatch_res != {}:
            logger.debug("Pmatch result {}".format(pmatch_res))
            return caspy.numeric.numeric.Numeric(pmatch_res["a"],"number")
        elif self.arg == caspy.numeric.numeric.Numeric(1,"number"):
            # Check if argument is just 1
            return caspy.numeric.numeric.Numeric(0,"number")
        else:
            return super().eval()
