import logging
import copy
from caspy.functions.function import Function1Arg
from caspy.printing import latex_numeric as ln
from caspy.numeric.symbol import Symbol
from caspy.numeric.numeric import Numeric
from caspy.numeric.fraction import Fraction
from caspy.factorise import factoriseNum

logger = logging.getLogger(__name__)


class Sqrt(Function1Arg):
    # TODO define ranges for functions
    fname = "sqrt"

    def __init__(self, x):
        self.arg = x

    def latex_format(self):
        return "\\sqrt{{{}}}".format(ln.latex_numeric_str(self.arg))

    def eval(self):
        if self.arg.is_exclusive_numeric():
            logger.debug("Attempting to simplify {} for sqrt".format(self.arg))
            if len(self.arg.val) > 1:
                logger.warning("Argument {} is exclusively numeric but"
                               "contains more than 1 symbol. Not trying"
                               "to simplify").format(self.arg)
            else:
                # Make a copy of the argument value in case the fraction
                # evaluated doesn't give a nice fraction representation
                sym = copy.deepcopy(self.arg.val[0])
                # Attempt to simplify
                # Removing this breaks sqrt(1/4) for example?!?!
                sym.simplify()
                logger.debug("Symbol {}".format(sym))

                if sym.is_zero():
                    return Numeric(0,"number")

                frac = sym.sym_frac_eval()

                if frac.is_int_frac():
                    surd_den = frac.den
                    # Sym is a fraction. Multiply it by den/den Fraction to
                    # ensure you don't end up with a surd on the bottom
                    factors = factoriseNum(frac.num*surd_den)
                    f_out = 1
                    surd = 1
                    logger.debug("Factors {}".format(factors))
                    if factors != [] and int(frac.den) == frac.den:
                        for f in set(factors):
                            # Only looks at each factor once
                            cnt_f = factors.count(f)
                            if cnt_f % 2 == 0:
                                # Even amount of occurences of factors so factor
                                # them all out
                                f_out *= f ** (cnt_f//2)
                            elif cnt_f > 1:
                                # Must be an odd amount of occurences of factor
                                f_out *= f ** ((cnt_f - 1)//2)
                                surd *= f
                            else:
                                surd *= f
                        logger.debug("Simplified to {} * sqrt({})".format(
                            f_out,surd
                        ))
                        if surd == 1:
                            # It's just 1 inside the surd so just return the
                            # f_out as a symbol
                            return Numeric(f_out,"number")
                        self.arg = surd
                        new_num = Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")
                        scalar = Symbol(1,Fraction(f_out,surd_den))
                        new_num.mul(Numeric(scalar,"sym_obj"))
                        # new_num.val.append(Symbol(Fraction(f_out,1),1))
                        return new_num

        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")
