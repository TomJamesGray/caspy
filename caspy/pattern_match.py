import logging
from caspy.parsing import parser as P
from caspy.numeric.numeric import Num

logger = logging.getLogger(__name__)


class PlaceholderVal:
    pass


class ConstPlaceholder(PlaceholderVal):
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return "<Constant placeholder>"


def pmatch(pat: Num, expr: Num):
    out = {}
    # Simplify both expressions
    pat.simplify()
    expr.simplify()

    logger.info("Pattern matching {} with expr {}".format(pat,expr))

    for expr_sym in expr.val:
        for pat_sym in pat.val:
            if pat_sym.contains_sym(expr_sym):
                logger.info("Symbol {} contains {}".format(pat_sym,expr_sym))
            else:
                logger.info("Symbol {} doesn't contain {}".format(pat_sym, expr_sym))

    return out


def pat_construct(pat: str, coeffs: dict) -> Num:
    """
    Constructs a pattern for use in pmatch
    :param pat: String containing an expression like "a*pi"
    :param coeffs: Dict storing information about the placeholder terms
    :return: Numeric object
    """
    # Evaluate the given pattern string
    parser = P.Parser()
    pat_eval = parser.parse(pat)
    # Replace the given coefficents
    for coeff in coeffs:
        if coeffs[coeff] == "const":
            pat_eval.replace(coeff, ConstPlaceholder(coeff))

    return pat_eval
