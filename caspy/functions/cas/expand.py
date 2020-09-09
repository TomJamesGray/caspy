import logging
import copy
import caspy.numeric.symbol
import caspy.pattern_match as pm
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg
from caspy.functions import trigonometric as trig
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


class ExpandTrig(Function1Arg):
    fname = "expand_trig"
    latex_fname = "expand_trig"

    def __init__(self,arg,expand_result=True):
        self.arg = arg
        self.expand_result = expand_result

    def eval(self):
        tot = num.Numeric(0, "number")
        for sym in self.arg.val:
            sin_id = False
            cos_id = False
            pmatch_res_sin = pm.pmatch_sym("B1*sin(A1)", {"A1": "rem","B1":"coeff"}, sym)
            if pmatch_res_sin == {}:
                # Try pmatch with cos
                pmatch_res_cos = pm.pmatch_sym("B1*cos(A1)", {"A1": "rem", "B1": "coeff"}, sym)
                if pmatch_res_cos != {}:
                    cos_id = True
                    pmatch_res = pmatch_res_cos
            else:
                sin_id = True
                pmatch_res = pmatch_res_sin

            if sin_id or cos_id:
                # Expand a trigonometric term
                if len(pmatch_res["A1"].val) == 1:
                    coeff = pmatch_res["A1"].val[0].coeff
                    coeff_r = coeff.to_real()
                    # Don't try and expand it when it's not an int coeff
                    if coeff_r == int(coeff_r) and abs(coeff_r) > 1:
                        sym_arg = copy.deepcopy(pmatch_res["A1"])
                        sym_uni = copy.deepcopy(sym_arg) / num.Numeric(coeff,"number")
                        # Get the representation of the symbol without the
                        # coeff
                        sym_uni.simplify()
                        b_val = num.Numeric(coeff_r - 1, "number") * copy.deepcopy(sym_uni)

                        if sin_id:
                            # Expand using identity:
                            # sin(a+b) = sin(a)cos(b)+cos(a)sin(b)
                            s1 = trig.Sin(sym_uni).eval()
                            c1 = trig.Cos(b_val).eval()
                            c2 = trig.Cos(sym_uni).eval()
                            s2 = ExpandTrig(trig.Sin(copy.deepcopy(b_val)).eval(), False).eval()
                            tot += pmatch_res["B1"] * (s1*c1 + c2*s2)
                            # Go onto next term
                            continue
                        else:
                            # Expand using identity:
                            # cos(a+b) = cos(a)cos(b)-sin(a)sin(b)
                            c1 = trig.Cos(sym_uni).eval()
                            c2 = ExpandTrig(trig.Cos(copy.deepcopy(b_val)).eval(), False).eval()
                            s1 = trig.Sin(sym_uni).eval()
                            s2 = ExpandTrig(trig.Sin(copy.deepcopy(b_val)).eval(), False).eval()
                            tot += pmatch_res["B1"] * (c1 * c2 - s1 * s2)
                            # Go onto next term
                            continue

            tot += num.Numeric(sym,"sym_obj")
        if self.expand_result:
            return Expand(tot).eval()
        return tot

