import logging
import itertools
import copy
import caspy.pattern_match
import caspy.parsing.parser
from caspy.helpers.helpers import polyn_div
from caspy.matrix import mat_mul,invert_mat,mat_vec_prod
from caspy.functions.function import Function1Arg
from caspy.helpers.helpers import lcm,gcd_l,get_divisors
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from caspy.factorise import factoriseNum

logger = logging.getLogger(__name__)

MAX_FLOAT_ERROR = 1e-5


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


def close_to_all_ints(x):
    for i in x:
        # Just comparing to int(i) can cause issues with floats
        # that are near but not exactly equal
        if abs(i - round(i)) > MAX_FLOAT_ERROR:
            return False
    return True


def close_to_zero_vec(x):
    for i in x:
        # Just comparing to int(i) can cause issues with floats
        # that are near but not exactly equal
        if abs(i) > MAX_FLOAT_ERROR:
            return False
    return True


def kronecker(polyn):
    M,v_polyn = kronecker_frac_to_int(polyn)
    cont = gcd_l(v_polyn)
    # Get primitive polynomial, ie remove common factors
    v_polyn_pp = [x // cont for x in v_polyn]
    return cont,M,kronecker_int(v_polyn_pp)


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


def is_const_polyn(polyn):
    return close_to_zero_vec(polyn[:-1])


def kronecker_int(polyn):
    logger.debug("Int factorising: {}".format(polyn))
    n = len(polyn) - 1
    if n <= 1:
        # Don't try and factor linear term
        return [polyn]

    logger.debug("v : {}".format(polyn))
    # Now have a polynomial in Z[x]
    logger.debug("n: {}".format(n))
    s = int(n/2)

    non_zeroes = []
    x_i = 0
    while len(non_zeroes) <= s:
        polyn_evaled = polyn_eval(polyn,x_i)
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


    # Generate matrix with the chosen x values to solve the linear equations
    mat_rows = []
    for x_val, func_val in non_zeroes:
        mat_rows.append([
            x_val ** power for power in range(s + 1)
        ])
    inv_mat = invert_mat(mat_rows)

    for rhs in itertools.product(*f_factors):
        q_polyn = mat_vec_prod(inv_mat,rhs)[::-1]
        # Check q is all integers and is not just a const
        if not close_to_all_ints(q_polyn) or is_const_polyn(q_polyn):
            continue
        quotient_2,remainder_2 = polyn_div(polyn,q_polyn)
        if close_to_zero_vec(remainder_2):
            # Ensure the quotient is just made up of integers
            if close_to_all_ints(quotient_2):
                # We have found divisor
                logger.debug(
                    "Found quotient: {}\nq_polyn_2: {}\nRemainder: {}".format(quotient_2, q_polyn, remainder_2))
                # Factor quotient and q_polyn again to see if the answer can be
                # reduced further
                quotient_factored = kronecker_int([round(x) for x in quotient_2])
                q_polyn_factored = kronecker_int([round(x) for x in q_polyn])
                # quotient_factored = kronecker_int(list(quotient_2.astype(int)))
                # q_polyn_factored = kronecker_int(list(q_polyn.astype(int)))
                logger.debug("Factored: {} {}".format(quotient_factored,q_polyn_factored))
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
        terms_used = []
        for i,sym in enumerate(self.arg.val):
            pmatch_res = caspy.pattern_match.pmatch_sym("A1*{}^N1".format(self.wrt),
                                                        {"N1":"const","A1":"const"},sym)
            if "A1" in pmatch_res.keys() and "N1" in pmatch_res.keys():
                if pmatch_res["N1"].to_real() == int(pmatch_res["N1"]) and \
                        pmatch_res["A1"].is_int_frac():
                    polyn.append([pmatch_res["A1"], int(pmatch_res["N1"])])
                    terms_used.append(i)

            elif sym.is_exclusive_numeric():
                try:
                    c = sym.sym_frac_eval()
                    if c.is_int_frac():
                        polyn.append([c,0])
                        terms_used.append(i)
                except Exception:
                    logger.critical("FAIL")

        output_val = []
        if len(polyn) > 0:
            empty_polyn = False
            # Get degree of polynomial
            n = max(polyn,key=lambda x:x[1])[1]
            # Convert polynomial so it's stored like
            # [coeff nth power, coeff n-1st power,...,constant term]
            polyn_to_factor = [Fraction(0,1) for i in range(n+1)]
            for coeff, power in polyn:
                polyn_to_factor[n - power] = coeff

            print("Factorising {}".format(polyn_to_factor))

            cont,m_val,factored = kronecker(polyn_to_factor)
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
            output = parser.parse("{}/{} * {}".format(
                cont,m_val,"*".join(factors_str))
            )
        else:
            empty_polyn = True
            output = Numeric(0)
        for i,sym in enumerate(self.arg.val):
            if i not in terms_used:
                # Add on other terms to the output that we didn't try to factorise
                output_val.append(copy.deepcopy(sym))
        if empty_polyn:
            output.val = output_val
        else:
            output.val = output.val + output_val

        return output
