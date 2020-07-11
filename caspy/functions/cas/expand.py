import logging
import copy
import caspy.numeric.symbol
from caspy.numeric.fraction import Fraction
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
            sym_tot = num.Numeric(1,"number")
            for (sym_name,sym_pow) in sym.val:
                if type(sym_name) == num.Numeric:
                    if sym_pow.is_exclusive_numeric():
                        frac_pow = sym_pow.frac_eval()
                        frac_pow.simplify()
                        logger.debug("On sym {}".format(sym_name))
                        if frac_pow.den == 1 and int(frac_pow.num) == frac_pow.num:
                            # Can expand this term
                            logger.debug("Expanding term {} to the power {}\n".
                                         format(sym_name,frac_pow))
                            if frac_pow.to_real() < 0:
                                take_recip = True
                                iters = int(abs(frac_pow.to_real())) - 1
                            else:
                                take_recip = False
                                iters = int(frac_pow.to_real()) - 1

                            cur_val = copy.deepcopy(sym_name)
                            mul_by = copy.deepcopy(sym_name)

                            for i in range(0,iters):
                                cur_val = cur_val.mul_expand(mul_by)

                            if take_recip:
                                sym_tot = sym_tot.mul_expand(cur_val.recip())
                            else:
                                sym_tot = sym_tot.mul_expand(cur_val)
                        else:
                            # Can't expand this term
                            new_pow = caspy.numeric.symbol.Symbol(1,frac_pow)
                            new_pow_num = num.Numeric(new_pow,"sym_obj")
                            logger.debug("Not expanding. Multiply sym_tot by {} ^ {}".format(sym_name,sym_pow))
                            sym_tot = sym_tot * (sym_name ** new_pow_num)
                    else:
                        # Can't expand this term
                        sym_tot = sym_tot * (sym_name ** sym_pow)
                else:
                    # Symbol name isn't numeric type, so could just be
                    # 'x' or a number for example, so append it to the symbols
                    # in the sym_tot value
                    for sym_term in sym_tot.val:
                        sym_term.val.append([sym_name,sym_pow])

            tot += sym_tot

        return tot
