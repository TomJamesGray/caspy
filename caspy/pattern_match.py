import logging
from caspy.parsing import parser as P
from caspy.numeric.numeric import Num

logger = logging.getLogger(__name__)


def pmatch(pat: str, expr: Num, coeffs: dict):
    # Evaluate the given pattern
    out = {}
    parser = P.Parser()
    pat_eval = parser.parse(pat)

    for expr_sym in expr.val:
        expr_sym.simplify()
        sym_eq = True
        for pat_sym in pat_eval.val:
            pat_sym.simplify()
            for (pat_sym_name,pat_pow) in pat_sym.val:
                sym_part_eq = True

                for (expr_sym_name,expr_pow) in expr_sym.val:
                    if type(pat_sym_name) == str:
                        if coeffs.get(pat_sym_name,False) == "const"\
                                and type(expr_sym_name) != str:
                            # Match ?!
                            sym_part_eq = True
                            out[pat_sym_name] = expr_sym_name
                            break
                    elif pat_sym_name == expr_sym_name and pat_pow == expr_pow:
                        sym_part_eq = True
                        break

                if not sym_part_eq:
                    return False
        if not sym_eq:
            return False

    return out