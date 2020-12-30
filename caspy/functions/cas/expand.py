import logging
import copy
import caspy.numeric.symbol
import caspy.pattern_match as pm
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg
from caspy.functions import trigonometric as trig
from caspy.numeric import numeric as num
from caspy.printing.latex_numeric import latex_numeric_str as lns

logger = logging.getLogger(__name__)


class Expand(Function1Arg):
    """Function to expand a numeric object like (1+x)^5"""
    fname = "expand"
    latex_fname = "expand"

    def __init__(self, x, recurse_into=True):
        self.arg = x
        self.recurse_into = recurse_into

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

                            if self.recurse_into:
                                new_sym_name = num.Numeric(0,"number")
                                for sym_in_sym_name in copy.deepcopy(sym_name.val):
                                    logger.info("Checking recurse on {}".format(sym_in_sym_name))
                                    need_to_recurse = False
                                    for (a,b) in sym_in_sym_name.val:
                                        if type(a) == num.Numeric:
                                            need_to_recurse = True
                                            break

                                    if need_to_recurse:
                                        logger.debug("Recursing for expand fn")
                                        new_sym_name += Expand(
                                            num.Numeric(sym_in_sym_name),True).eval()
                                    else:
                                        new_sym_name += num.Numeric(sym_in_sym_name)
                            else:
                                new_sym_name = sym_name

                            cur_val = copy.deepcopy(new_sym_name)
                            mul_by = copy.deepcopy(new_sym_name)

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
                    # 'x' or a number for example, so make it a symbol type and
                    # multiply it onto all values in sym_term
                    tmp_sym = caspy.numeric.symbol.Symbol(sym_name,Fraction(1,1))
                    for sym_term in sym_tot.val:
                        sym_term.mul(copy.deepcopy(tmp_sym))

            tot += sym_tot

        return tot


def sin_id_expand(a,b):
    # Expand using identity:
    # sin(a+b) = sin(a)cos(b)+cos(a)sin(b)
    s1 = trig.Sin(a).eval()
    c1 = ExpandTrig(trig.Cos(copy.deepcopy(b)).eval(), False).eval()
    c2 = trig.Cos(a).eval()
    s2 = ExpandTrig(trig.Sin(copy.deepcopy(b)).eval(), False).eval()
    return s1 * c1 + c2 * s2


def cos_id_expand(a,b):
    # Expand using identity:
    # cos(a+b) = cos(a)cos(b)-sin(a)sin(b)
    c1 = trig.Cos(a).eval()
    c2 = ExpandTrig(trig.Cos(copy.deepcopy(b)).eval(), False).eval()
    s1 = trig.Sin(a).eval()
    s2 = ExpandTrig(trig.Sin(copy.deepcopy(b)).eval(), False).eval()
    return c1 * c2 - s1 * s2


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
                            tot += pmatch_res["B1"] * sin_id_expand(sym_uni,b_val)
                            # Go onto next term
                            continue
                        else:
                            tot += pmatch_res["B1"] * cos_id_expand(sym_uni,b_val)
                            # Go onto next term
                            continue
                else:
                    # Expand term by term
                    a_val = num.Numeric(copy.deepcopy(pmatch_res["A1"].val[0]),"sym_obj")
                    b_val = copy.deepcopy(pmatch_res["A1"]) - copy.deepcopy(a_val)
                    logger.debug("Expanding term by term; a: {} b: {}".format(
                        a_val,b_val
                    ))
                    if sin_id:
                        tot += pmatch_res["B1"] * sin_id_expand(
                            a_val,b_val
                        )
                        continue
                    else:
                        tot += pmatch_res["B1"] * cos_id_expand(
                            a_val, b_val
                        )
                        continue

            tot += num.Numeric(sym,"sym_obj")
        if self.expand_result:
            logger.info("Pre expanding {}".format(lns(tot)))
            xyz = Expand(tot,True).eval()
            logger.info("Expanding result {}".format(lns(xyz)))
            return xyz
        return tot


