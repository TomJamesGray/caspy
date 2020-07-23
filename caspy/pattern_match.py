"""
Pattern matching module. Patterns need to be generated using the pat_construct
function. The placeholders to be used in the describing dict and the corresponding
classes used to represent them in the numeric object are

const - Numeric constant that can be zero -> ConstPlaceholder
const_non_zero - Numeric constant that can't be zero -> ConstPlaceholderNonZero
coeff - Numeric symbol that can contain things that aren't numeric
        for instance if the pattern is a*x then if the expression is
        5*x*y*cos(z) a would be 5*y*cos(z) -> CoeffPlaceholder
"""
import logging
import caspy.parsing
import caspy.numeric.numeric
import caspy.numeric.symbol
from caspy.numeric.fraction import Fraction

logger = logging.getLogger(__name__)


class PlaceholderVal:
    def __init__(self, name):
        self.name = name


class ConstPlaceholder(PlaceholderVal):
    def __repr__(self):
        return "<Constant placeholder>"


class ConstPlaceHolderNonZero(PlaceholderVal):
    def __repr__(self):
        return "<Constant placeholder non zero>"


class CoeffPlaceholder(PlaceholderVal):
    def __repr__(self):
        return "<Coefficient placeholder>"


def does_numeric_contain_placeholders(x) -> bool:
    """
    Checks if a numeric object contains any placeholders
    :param x: Numeric object
    :return: Boolean
    """
    for sym in x.val:
        for sym_name,sym_pow in sym.val:
            if isinstance(sym_name,PlaceholderVal):
                return True
            if type(sym_pow) == caspy.numeric.numeric.Numeric:
                if not does_numeric_contain_placeholders(sym_pow):
                    return True
    return False


def pmatch(pat, expr):
    """
    Tries to match a pattern generated in pat_construct to a given expression
    :param pat: Numeric object with some Placeholder objects
    :param expr: Numeric object
    :return: A tuple: (dict with keys as Placeholder names, the matching numeric
    expression). In effect the second term is just the expr input, but it is
    there for recursive purposes
    """
    out = {}
    used_terms = []
    # Simplify both expressions
    pat.simplify()
    expr.simplify()

    logger.info("Pattern matching {} with expr {}".format(pat, expr))

    attempted_match_sum = caspy.numeric.numeric.Numeric(0,"number")
    for pat_sym in pat.val:
        for i, expr_sym in enumerate(expr.val):
            # Attempt to match this pattern sym with this expression sym
            # Initialise a blank symbol with value 1
            attempted_match_sym = caspy.numeric.symbol.Symbol(1,Fraction(1,1))
            # Make a temporary dict to store the names of coefficients used
            # and their values in this attempt. If the symbols match then we
            # transfer these values to the actual out dict
            tmp_out = {}
            for (pat_sym_fact_name, pat_sym_fact_pow) in pat_sym.val:

                if type(pat_sym_fact_name) == ConstPlaceholder:
                    tmp_out[pat_sym_fact_name.name] = expr_sym.coeff
                    # Multiply the attempted_match_sym by the coeff
                    coeff_tmp_sym = caspy.numeric.symbol.Symbol(1,expr_sym.coeff)
                    attempted_match_sym = attempted_match_sym * coeff_tmp_sym
                    logger.debug("Multiply coefficient {} onto match_sym".format(expr_sym.coeff))
                    used_terms.append(i)

                # TODO dealing with functions
                elif type(pat_sym_fact_name) == str:
                    if type(pat_sym_fact_pow) == caspy.numeric.numeric.Numeric:
                        if not does_numeric_contain_placeholders(pat_sym_fact_pow):
                            used_terms.append(i)
                            # Can just multiply this term onto the match_sym val
                            attempted_match_sym.val.append([pat_sym_fact_name,
                                                            pat_sym_fact_pow])
                            logger.debug("Multiplying term {}^{} onto "
                                         "match_sym".format(pat_sym_fact_name,pat_sym_fact_pow))
                        else:
                            # Find matching term
                            for j, expr_sym_fact in enumerate(expr_sym.val):
                                if expr_sym_fact[0] == pat_sym_fact_name and \
                                        expr_sym_fact[1].all_syms_eq(pat_sym_fact_pow):
                                    # Matching term found, therefore turn the
                                    # powers into Numeric objects and run pmatch
                                    logger.debug("RECURSING WITH {} AND {}".format(pat_sym_fact_pow,expr_sym_fact[1]))
                                    pmatch_res,num_pow = pmatch(pat_sym_fact_pow,expr_sym_fact[1])
                                    logger.debug("Recursed pmatch result {}".format(pmatch_res))
                                    # TODO refactor so it uses tmp_out possibly?
                                    # would require returning the attempted_match_sym
                                    tmp_out.update(pmatch_res)
                                    used_terms.append(i)
                                    attempted_match_sym.val.append([
                                        pat_sym_fact_name,
                                        num_pow
                                    ])
                                    break

            if attempted_match_sym == expr_sym and \
                attempted_match_sym.coeff == expr_sym.coeff:
                logger.debug("Updating out dict")
                # Have matched it successfully so can update the out dict
                # TODO testing for when the same placeholder appears multiple
                # times in patter, ie stuff like a*x^2 + a*y^2
                out.update(tmp_out)
                break
            else:
                logger.debug("Can't update out dict "
                             "attempted_match_sym {} == expr_sym {} returns  {}".format(
                    attempted_match_sym,expr_sym,attempted_match_sym == expr_sym
                ))
        attempted_match_sum = attempted_match_sum + \
                              caspy.numeric.numeric.Numeric(attempted_match_sym,"sym_obj")

    if list(sorted(set(used_terms))) != list(range(0, len(expr.val))):
        return {}, None

    return out, attempted_match_sum


def pat_construct(pat: str, coeffs: dict):
    """
    Constructs a pattern for use in pmatch
    :param pat: String containing an expression like "a*pi"
    :param coeffs: Dict storing information about the placeholder terms
    :return: Numeric object
    """
    # Evaluate the given pattern string
    parser = caspy.parsing.parser.Parser()
    pat_eval = parser.parse(pat)
    # Replace the given coefficents
    for coeff in coeffs:
        if coeffs[coeff] == "const":
            pat_eval.replace(coeff, ConstPlaceholder(coeff))
        elif coeffs[coeff] == "const_non_zero":
            pat_eval.replace(coeff, ConstPlaceHolderNonZero(coeff))
        elif coeffs[coeff] == "coeff":
            pat_eval.replace(coeff, CoeffPlaceholder(coeff))

    return pat_eval
