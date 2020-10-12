import logging
import caspy.pattern_match
from caspy.functions.function import Function1Arg
from caspy.helpers.helpers import lcm,gcd_l,get_divisors
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from caspy.factorise import factoriseNum

logger = logging.getLogger(__name__)


def polyn_eval(polyn,x):
    val = 0
    for coeff,power in polyn:
        val += coeff * x ** power
    return val


def kronecker(polyn):
    """
    Factorises a single variable polynomial with Kroneckers method.
    The polynomial is represented by a list eg u=a_0 + a_1 * x + ... is
    represented by [[a_0,0], [a_1,1], ...]
    :return: Multiple lists representing the polynomial factors
    """
    denominators = []
    for coeff,_ in polyn:
        denominators.append(coeff.den)
    M = lcm(denominators)
    logger.debug("Kronecker M: {}".format(M))

    v_polyn = []
    coeffs = []
    for coeff,power in polyn:
        new_coeff = int(coeff.to_real() * M)
        v_polyn.append([new_coeff,int(power)])
        coeffs.append(new_coeff)

    cont = gcd_l(coeffs)
    logger.debug("cont : {}".format(cont))
    logger.debug("v : {}".format(v_polyn))
    # Now have a polynomial in Z[x]
    n = max(*v_polyn,key=lambda x: x[1])[1]
    logger.debug("n: {}".format(n))
    s = int(n/2)

    non_zeroes = []
    x_i = 0
    while len(non_zeroes) <= s:
        polyn_evaled = polyn_eval(v_polyn,x_i)
        if polyn_evaled != 0:
            non_zeroes.append([x_i,polyn_evaled])
        x_i += 1

    logger.debug("x_i : {}".format(non_zeroes))

    f_factors = []
    for _,f_val in non_zeroes:
        divisors_abs = list(get_divisors(abs(f_val)))
        f_factors.append(
            divisors_abs + [-1 * fact for fact in divisors_abs]
        )
    logger.debug("S_i: {}".format(f_factors))

    pass


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
                if pmatch_res["N1"].to_real() == int(pmatch_res["N1"]) and \
                        pmatch_res["A1"].is_int_frac():
                    polyn.append([pmatch_res["A1"], int(pmatch_res["N1"])])

            elif sym.is_exclusive_numeric():
                try:
                    c = sym.sym_frac_eval()
                    if c.is_int_frac():
                        polyn.append([c,Fraction(0,1)])
                except Exception:
                    logger.critical("FAIL")

        factored = kronecker(polyn)
        logger.critical("Repr: {}".format(polyn))
        return super().eval()
