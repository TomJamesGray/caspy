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
from caspy.numeric.numeric import Num

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


def pmatch(pat: Num, expr: Num):
    """
    Tries to match a pattern generated in pat_construct to a given expression
    :param pat: Numeric object with some Placeholder objects
    :param expr: Numeric object
    :return: Dict with keys as Placeholder names
    """
    out = {}
    used_terms = []
    # Simplify both expressions
    pat.simplify()
    expr.simplify()

    logger.info("Pattern matching {} with expr {}".format(pat,expr))

    for i,expr_sym in enumerate(expr.val):
        for pat_sym in pat.val:
            if pat_sym.contains_sym(expr_sym):
                logger.info("Symbol {} contains {}".format(pat_sym,expr_sym))
                used_terms.append(i)
                # Find the placeholder
                for (pat_sym_name,pat_sym_pow) in pat_sym.val:
                    if type(pat_sym_name) == ConstPlaceholder:
                        # Extract coefficient of expr_sym
                        out[pat_sym_name.name] = expr_sym.coeff
            else:
                logger.info("Symbol {} doesn't contain {}".format(pat_sym, expr_sym))
    print("OUT {} USED_TERMS {}".format(out,used_terms))
    if sorted(used_terms) != list(range(0,len(expr.val))):
        return {}

    return out


def pat_construct(pat: str, coeffs: dict) -> Num:
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
