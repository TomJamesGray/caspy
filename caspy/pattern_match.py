"""
Pattern matching module. Patterns need to be generated using the pat_construct
function. The placeholders to be used in the describing dict and the corresponding
classes used to represent them in the numeric object are

const - Numeric constant that can be zero -> ConstPlaceholder
const_non_zero - Numeric constant that can't be zero -> ConstPlaceholderNonZero
coeff - Numeric symbol that can contain things that aren't numeric
        for instance if the pattern is a*x then if the expression is
        5*x*y*cos(z) a would be 5*y*cos(z) -> CoeffPlaceholder
rem - Collects any terms that aren't used -> RemainingPlaceholder
"""
import logging
import copy
import caspy.parsing
import caspy.numeric.numeric
import caspy.numeric.symbol
import caspy.functions.function
import caspy.parsing.simplify_output
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


class RemainingPlaceholder(PlaceholderVal):
    def __repr__(self):
        return "<Remaining placeholder>"


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


def pmatch_sym(pat, pat_dict, sym):
    """
    Simple helper function to run pattern match on a symbol
    :param pat: Pattern string to be passed to pat_construct
    :param pat_dict: Dictionary of placeholders for pat_construct
    :param sym: The symbol object to have pmatch run on it
    :return:
    """
    pat = pat_construct(pat, pat_dict)
    numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
    pmatch_res, _ = pmatch(pat, numeric_wrapper)
    return pmatch_res


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
    remaining_placeholder_name = None
    # Simplify both expressions
    pat.simplify()
    expr.simplify()

    logger.info("Pattern matching {} with expr {}".format(pat, expr))

    attempted_match_sum = caspy.numeric.numeric.Numeric(0,"number")
    for pat_sym in pat.val:
        sym_done = False
        for i, expr_sym in enumerate(expr.val):
            # Attempt to match this pattern sym with this expression sym
            # Initialise a blank symbol with value 1
            attempted_match_sym = caspy.numeric.symbol.Symbol(1,Fraction(1,1))
            syms_added_from_pat = caspy.numeric.symbol.Symbol(1,Fraction(1,1))
            # Make a temporary dict to store the names of coefficients used
            # and their values in this attempt. If the symbols match then we
            # transfer these values to the actual out dict
            tmp_out = {}
            unused_expression_factors_name = None
            used_expression_factors = []
            logger.debug("Expr sym is {}".format(expr_sym))
            for (pat_sym_fact_name, pat_sym_fact_pow) in pat_sym.val:
                if type(pat_sym_fact_name) == ConstPlaceholder:
                    tmp_out[pat_sym_fact_name.name] = expr_sym.coeff
                    # Multiply the attempted_match_sym by the coeff
                    coeff_tmp_sym = caspy.numeric.symbol.Symbol(1,expr_sym.coeff)
                    attempted_match_sym = attempted_match_sym * coeff_tmp_sym
                    logger.debug("Multiply coefficient {} onto match_sym".format(expr_sym.coeff))
                    used_terms.append(i)
                    used_expression_factors.append(expr_sym.get_coeff_index())

                elif type(pat_sym_fact_name) == RemainingPlaceholder:
                    # Set a flag so remaining terms will be included in out dict
                    # once all other terms have been matched
                    remaining_placeholder_name = pat_sym_fact_name.name

                elif type(pat_sym_fact_name) == CoeffPlaceholder:
                    unused_expression_factors_name = pat_sym_fact_name.name

                elif type(pat_sym_fact_name) == str:
                    if type(pat_sym_fact_pow) == caspy.numeric.numeric.Numeric:
                        if not does_numeric_contain_placeholders(pat_sym_fact_pow):
                            used_terms.append(i)
                            # Can just multiply this term onto the match_sym val
                            attempted_match_sym.val.append([pat_sym_fact_name,
                                                            pat_sym_fact_pow])
                            # Multiply this term onto syms_added_from_pat
                            # so it won't appear twice if we are using a
                            # CoeffPlaceholder
                            syms_added_from_pat.val.append([
                                pat_sym_fact_name,
                                pat_sym_fact_pow])

                            logger.debug("Multiplying term {}^{} onto "
                                         "match_sym".format(pat_sym_fact_name,pat_sym_fact_pow))
                        else:
                            # Find matching term
                            for j, expr_sym_fact in enumerate(expr_sym.val):
                                if expr_sym_fact[0] == pat_sym_fact_name:
                                    # Matching term found, therefore turn the
                                    # powers into Numeric objects and run pmatch
                                    logger.debug("RECURSING WITH {} AND {}".format(pat_sym_fact_pow,expr_sym_fact[1]))
                                    pmatch_res,num_pow = pmatch(pat_sym_fact_pow,expr_sym_fact[1])
                                    logger.debug("Recursed pmatch result {}".format(pmatch_res))
                                    tmp_out.update(pmatch_res)
                                    used_terms.append(i)
                                    used_expression_factors.append(j)
                                    attempted_match_sym.val.append([
                                        pat_sym_fact_name,
                                        num_pow
                                    ])
                                    break

                elif isinstance(pat_sym_fact_name,caspy.functions.function.Function):
                    # TODO checking numeric powers
                    if not does_numeric_contain_placeholders(pat_sym_fact_name.arg):
                        used_terms.append(i)
                        # Can just multiply this term onto the match_sym val
                        attempted_match_sym.val.append([pat_sym_fact_name,
                                                        pat_sym_fact_pow])
                        logger.debug("Multiplying term {}^{} onto "
                                     "match_sym".format(pat_sym_fact_name, pat_sym_fact_pow))
                    else:
                        # Find matching term
                        logger.debug("Trying to find matching term")
                        for j, expr_sym_fact in enumerate(expr_sym.val):
                            logger.debug("Matching {} with {}".format(pat_sym_fact_name,expr_sym_fact))
                            if not isinstance(expr_sym_fact[0],caspy.functions.function.Function):
                                continue

                            if expr_sym_fact[0].fname == pat_sym_fact_name.fname \
                                    and expr_sym_fact[1] == pat_sym_fact_pow:
                                # Matching term found, therefore pmatch the
                                # funtion arguments
                                logger.info("Recursing with {} and {}".format(
                                    pat_sym_fact_name.arg, expr_sym_fact[0].arg
                                ))
                                pmatch_res, pmatch_res_arg = pmatch(
                                    pat_sym_fact_name.arg, expr_sym_fact[0].arg
                                )
                                logger.info("Recursed pmatch result {} resulting arg {}".format(
                                    pmatch_res,pmatch_res_arg))

                                tmp_out.update(pmatch_res)
                                used_terms.append(i)
                                used_expression_factors.append(j)
                                # TODO maybe define fns dict somewhere else
                                if expr_sym_fact[0].fname in caspy.parsing.simplify_output.fns:
                                    new_fn_obj = caspy.parsing.simplify_output.fns[expr_sym_fact[0].fname](
                                        pmatch_res_arg)
                                attempted_match_sym.val.append([
                                    new_fn_obj,
                                    pat_sym_fact_pow
                                ])
                                break

            # Use up remaining factors of the expression symbol if we have
            # encountered a CoeffPlaceholder object
            if unused_expression_factors_name is not None:
                logger.debug("syms_added_from_pat {}".format(syms_added_from_pat))
                logger.debug("Attempted match sym {}".format(attempted_match_sym))
                unused_factors_prod = caspy.numeric.symbol.Symbol(1,Fraction(1,1))
                for k, expression_factor in enumerate(expr_sym.val):
                    if k not in used_expression_factors:
                        unused_factors_prod.val.append(copy.deepcopy(expression_factor))

                logger.debug("unused_factors_prod {}".format(unused_factors_prod))
                unused_factors_prod = unused_factors_prod / copy.deepcopy(syms_added_from_pat)
                unused_factors_prod.simplify()
                logger.debug("Coeff val {}".format(unused_factors_prod))
                tmp_out.update({
                    unused_expression_factors_name:caspy.numeric.numeric.Numeric(unused_factors_prod,"sym_obj")
                })
                attempted_match_sym = attempted_match_sym * unused_factors_prod

            if attempted_match_sym == expr_sym and \
                    attempted_match_sym.coeff == expr_sym.coeff:
                logger.debug("Updating out dict")
                # Have matched it successfully so can update the out dict
                # TODO testing for when the same placeholder appears multiple
                # times in patter, ie stuff like a*x^2 + a*y^2
                out.update(tmp_out)
                # Break out of this loop as the symbol has been matched
                sym_done = True
                break
            else:
                logger.info("Can't update out dict "
                            "attempted_match_sym {} == expr_sym {} returns  {}".format(
                    attempted_match_sym,expr_sym,attempted_match_sym == expr_sym
                ))

        if sym_done:
            attempted_match_sum = attempted_match_sum + \
                                  caspy.numeric.numeric.Numeric(attempted_match_sym,"sym_obj")

    if remaining_placeholder_name is not None:
        remaining_numeric_obj = caspy.numeric.numeric.Numeric(0,"number")
        for i,sym in enumerate(expr.val):
            if i not in used_terms:
                sym_numeric_obj = caspy.numeric.numeric.Numeric(sym,"sym_obj")
                remaining_numeric_obj += sym_numeric_obj
        out[remaining_placeholder_name] = remaining_numeric_obj

        return out,expr

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
        elif coeffs[coeff] == "rem":
            pat_eval.replace(coeff, RemainingPlaceholder(coeff))

    return pat_eval
