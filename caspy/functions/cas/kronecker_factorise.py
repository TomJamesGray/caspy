import logging
import itertools
import numpy as np
import caspy.pattern_match
import caspy.parsing.parser
from caspy.functions.function import Function1Arg
from caspy.helpers.helpers import lcm,gcd_l,get_divisors
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from caspy.factorise import factoriseNum

logger = logging.getLogger(__name__)


def polyn_eval(polyn,x):
    val = 0
    n = len(polyn) - 1
    for i,coeff in enumerate(polyn):
        val += coeff * x ** (n-i)
    return val


def np_polyn_to(polyn):
    new_repr = []
    max_pow = len(polyn)-1
    for index,coeff in enumerate(polyn):
        if coeff != 0:
            new_repr.append([Fraction(int(coeff),1),max_pow-index])
    return new_repr


def kronecker(polyn):
    M,v_polyn = kronecker_frac_to_int(polyn)
    return kronecker_int(v_polyn)


def kronecker_frac_to_int(polyn):
    denominators = []
    for coeff in polyn:
        if coeff.num != 0:
            denominators.append(coeff.den)
    M = lcm(denominators)
    logger.debug("Kronecker M: {}".format(M))

    v_polyn = []
    for coeff in polyn:
        new_coeff = int(coeff.to_real() * M)
        v_polyn.append(new_coeff)

    return M, v_polyn


def kronecker_int(polyn):
    n = len(polyn) - 1
    if n <= 1:
        # Don't try and factor linear term
        return [polyn]

    v_polyn = polyn

    logger.debug("v : {}".format(v_polyn))
    cont = gcd_l(v_polyn)
    logger.debug("cont : {}".format(cont))
    # Now have a polynomial in Z[x]
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

    # Calucluate the divisors of the f(non_zeroes)
    f_factors = []
    for _,f_val in non_zeroes:
        divisors_abs = list(get_divisors(abs(f_val)))
        f_factors.append(
            divisors_abs + [-1 * fact for fact in divisors_abs]
        )
    logger.debug("S_i: {}".format(f_factors))

    # TODO implement own polynomial division algorithm

    # Generate matrix with the chosen x values to solve the linear equations
    mat_rows = []
    for x_val, func_val in non_zeroes:
        mat_rows.append([
            x_val ** power for power in range(s + 1)
        ])
    inv_mat = np.linalg.inv(np.array(mat_rows))

    for rhs in itertools.product(*f_factors):
        q_polyn = np.flipud(inv_mat.dot(np.array(rhs)))
        quotient,remainder = np.polydiv(v_polyn,q_polyn)
        if np.array_equal(remainder,np.array([0.])):
            # Ensure the quotient is just made up of integers
            if False not in np.equal(np.mod(quotient,1),0):
                # We have found divisor
                print("Found quotient: {}\nq_polyn: {}\nRHS: {}".format(quotient,q_polyn,rhs))
                # Factor quotient and q_polyn again to see if the answer can be
                # reduced further
                quotient_factored = kronecker_int(list(quotient.astype(int)))
                q_polyn_factored = kronecker_int(list(q_polyn.astype(int)))
                print("Factored: {} {}".format(quotient_factored,q_polyn_factored))
                return quotient_factored + q_polyn_factored
    # Couldn't factorise the polynomial
    return [polyn]


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
                        polyn.append([c,0])
                except Exception:
                    logger.critical("FAIL")

        # Get degree of polynomial
        n = max(polyn,key=lambda x:x[1])[1]
        # Convert polynomial so it's stored like
        # [coeff nth power, coeff n-1st power,...,constant term]
        polyn_to_factor = [Fraction(0,1) for i in range(n+1)]
        for coeff, power in polyn:
            polyn_to_factor[n - power] = coeff

        print("Factorising {}".format(polyn_to_factor))
        factored = kronecker(polyn_to_factor)
        if len(factored) > 1:
            factors_str = []
            for factor in factored:
                parts = []
                max_fact_pow = len(factor) - 1
                for i,coeff in enumerate(factor):
                    # TODO possibly refactor this so it doesn't make a string
                    # to be parsed?
                    parts.append("{}*{}^{}".format(
                        coeff,self.wrt,max_fact_pow - i
                    ))
                factors_str.append("({})".format("+".join(parts)))
            parser = caspy.parsing.parser.Parser()
            return parser.parse("*".join(factors_str))

        logger.critical("Repr: {}".format(factored))
        return super().eval()
