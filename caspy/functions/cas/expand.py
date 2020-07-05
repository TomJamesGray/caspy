import logging
import copy
from caspy.functions.function import Function1Arg
from caspy.numeric import numeric as num

logger = logging.getLogger(__name__)


class Expand(Function1Arg):
    """Function to expand a numeric object like (1+x)^5"""
    fname = "expand"
    latex_fname = "expand"

    def __init__(self,x):
        self.arg = x

    def eval(self):
        logger.debug("Attempting to expand {}".format(self.arg))
        tot = num.Numeric(0,"number")
        for sym in self.arg.val:
            for (sym_name,sym_pow) in sym.val:
                if type(sym_name) == num.Numeric:
                    if sym_pow.is_exclusive_numeric():
                        frac_pow = sym_pow.frac_eval()
                        frac_pow.simplify()
                        if frac_pow.den == 1:
                            # Can expand this term
                            logger.debug("Expanding term {} to the power {}\n".
                                         format(sym_name,frac_pow))
                            # TODO handling when it's to negative powers
                            cur_val = copy.deepcopy(sym_name)
                            mul_by = copy.deepcopy(sym_name)

                            for i in range(0,int(frac_pow.to_real())-1):
                                cur_val = cur_val.mul_expand(mul_by)

                            tot += cur_val

        return tot
