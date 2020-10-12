import logging
import caspy.pattern_match
from caspy.functions.function import Function1Arg
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction

logger = logging.getLogger(__name__)


class KroneckerFactor(Function1Arg):
    fname = "factor"
    latex_fname = "factor"

    def __init__(self,x):
        self.arg = x

    def eval(self):
        self.wrt = "x"
        # Store a representation of the polynomial as [[coeff1,power1],...]
        polyn = []
        for i,sym in enumerate(self.arg.val):
            pmatch_res = caspy.pattern_match.pmatch_sym("A1*{}^N1".format(self.wrt),
                                                        {"N1":"const","A1":"const"},sym)
            if "A1" in pmatch_res.keys() and "N1" in pmatch_res.keys():
                if pmatch_res["N1"].is_int_frac() and \
                        pmatch_res["A1"].is_int_frac():
                    polyn.append([pmatch_res["A1"], pmatch_res["N1"]])
            elif sym.is_exclusive_numeric():
                try:
                    c = sym.sym_frac_eval()
                    if c.is_int_frac():
                        polyn.append([c,Fraction(0,1)])
                except Exception:
                    logger.critical("FAIL")
        logger.critical("Repr: {}".format(polyn))
        return super().eval()
