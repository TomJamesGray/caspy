import logging
from copy import copy
import caspy.numeric.numeric
import caspy.pattern_match as pm
import caspy.parsing.parser
from caspy.functions.function import Function
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Differentiate(Function):
    """Caspy function to differentiate a numeric object symbolically"""
    fname = "diff"

    def __init__(self, arg, wrt="x"):
        self.arg = arg
        self.fully_diffed = False
        # Annoyingly the 'wrt' if provided will be a numeric object
        # so we need to extract the actual variable in question
        if type(wrt) == caspy.numeric.numeric.Numeric:
            if len(wrt.val) > 1:
                logger.critical("With respect to term contains "
                                "multiple symbols")
            else:
                set_wrt = False
                for (sym_fact_name,sym_fact_pow) in wrt.val[0].val:
                    if type(sym_fact_name) == str:
                        if not set_wrt:
                            self.wrt = sym_fact_name
                            set_wrt = True
                        else:
                            logger.critical("With respect to term contains "
                                            "multiple options for wrt property")
        else:
            self.wrt = wrt

    def latex_format(self):
        return "\\frac{{\\mathrm{{d}}}}{{\\mathrm{{d}}{}}} ({})".format(
            self.wrt,ln.latex_numeric_str(self.arg)
        )

    def eval(self):
        """
        Evaluates the derivative symbol by symbol
        :return: Numeric object
        """
        logger.debug("Attempting to differentiate {} wrt {}".format(self.arg,
                                                                    self.wrt))
        parser = caspy.parsing.parser.Parser()
        tot = caspy.numeric.numeric.Numeric(0, "number")
        diffed_values = []
        for i,sym in enumerate(self.arg.val):
            sym.simplify()
            if sym.is_exclusive_numeric() or not sym.has_variable_in(self.wrt):
                # Derivative of constant term is zero
                diffed_values.append(i)
                continue

            # Try matching x^n
            pat = pm.pat_construct("a*{}^n".format(self.wrt), {"n": "const", "a": "const"})
            numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
            pmatch_res, _ = pm.pmatch(pat, numeric_wrapper)
            if pmatch_res != {}:
                term_val = parser.parse("{} * {} ^ ({})".format(
                    copy(pmatch_res["a"]) * copy(pmatch_res["n"]),
                    self.wrt,
                    copy(pmatch_res["n"]) - 1
                ))
                tot += term_val
                diffed_values.append(i)
                continue

        new_val = []
        # Remove integrated values from the arg property
        for j, term_val in enumerate(self.arg.val):
            if j not in diffed_values:
                new_val.append(term_val)

        if new_val == []:
            # All terms have been integrated
            self.fully_diffed = True
            return tot
        else:
            # Make a numeric object to store the non integrated terms
            new_val_numeric_obj = caspy.numeric.numeric.Numeric(1, "number")
            new_val_numeric_obj.val = new_val
            self.arg = new_val_numeric_obj
            # Return integrated terms and other terms in an integral
            remaining_int = super().eval()
            return remaining_int + tot