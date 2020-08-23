import logging
from copy import copy
import caspy.numeric.numeric
import caspy.pattern_match as pm
import caspy.parsing.parser
import caspy.functions.trigonometric as trig
import caspy.functions.cas.expand as expand
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
                for (sym_fact_name, sym_fact_pow) in wrt.val[0].val:
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
            pmatch_res = pm.pmatch_sym("a*{}^n".format(self.wrt),
                                       {"n": "const", "a": "const"}, sym)
            if pmatch_res != {}:
                term_val = parser.parse("{} * {} ^ ({})".format(
                    copy(pmatch_res["a"]) * copy(pmatch_res["n"]),
                    self.wrt,
                    copy(pmatch_res["n"]) - 1
                ))
                tot += term_val
                diffed_values.append(i)
                continue

            # Try diffing sin terms
            pmatch_res = pm.pmatch_sym("A1*sin(A2)",
                                       {"A1": "const", "A2": "rem"}, sym)
            if pmatch_res != {}:
                logger.debug("Differentiating sin term")
                # Diff the argument
                d_obj = Differentiate(pmatch_res["A2"])
                derivative = d_obj.eval()
                if d_obj.fully_diffed:
                    derivative.simplify()
                    numeric_coeff = caspy.numeric.numeric.Numeric(
                        pmatch_res["A1"], "number"
                    )
                    cos_obj = caspy.numeric.numeric.Numeric(
                        trig.Cos(pmatch_res["A2"]), "sym"
                    )
                    term_val = numeric_coeff * derivative * cos_obj
                    tot += term_val
                    diffed_values.append(i)
                    continue

            # Try diffing cos terms
            pmatch_res = pm.pmatch_sym("A1*cos(A2)",
                                       {"A1": "const", "A2": "rem"}, sym)
            if pmatch_res != {}:
                logger.debug("Differentiating cos term")
                # Diff the argument
                d_obj = Differentiate(pmatch_res["A2"])
                derivative = d_obj.eval()
                if d_obj.fully_diffed:
                    derivative.simplify()
                    numeric_coeff = caspy.numeric.numeric.Numeric(
                        pmatch_res["A1"], "number"
                    ).neg()
                    cos_obj = caspy.numeric.numeric.Numeric(
                        trig.Sin(pmatch_res["A2"]), "sym"
                    )
                    term_val = numeric_coeff * derivative * cos_obj
                    tot += term_val
                    diffed_values.append(i)
                    continue

            # Try diffing ln terms
            pmatch_res = pm.pmatch_sym("A1*ln(A2)",
                                       {"A1": "const", "A2": "rem"}, sym)
            if pmatch_res != {}:
                logger.debug("Differentiating ln term")
                # Diff the argument
                d_obj = Differentiate(pmatch_res["A2"])
                derivative = d_obj.eval()
                if d_obj.fully_diffed:
                    derivative.simplify()
                    numeric_coeff = caspy.numeric.numeric.Numeric(
                        pmatch_res["A1"], "number"
                    )
                    term_val = numeric_coeff * derivative / pmatch_res["A2"]
                    tot += term_val
                    diffed_values.append(i)
                    continue

            # Try differentiating exponential terms
            pmatch_res = pm.pmatch_sym("A1 * e^(A2)".format(self.wrt),
                                    {"A1": "const", "A2": "rem"}, sym)
            if pmatch_res != {}:
                logger.debug("Differentiating exponential term, pmatch result {}".format(pmatch_res))
                # Currently pattern matching doesn't quite work correctly with matching
                # things like e^(a*x+b) so we will have to pattern match the A2 term
                exp_pow = expand.Expand(pmatch_res["A2"]).eval()
                pat = pm.pat_construct("B1 * {} + B2".format(self.wrt),
                                       {"B1": "const", "B2": "const"})
                pmatch_res_pow, _ = pm.pmatch(pat, exp_pow)
                logger.debug("Power pmatch result {}".format(pmatch_res_pow))
                if pmatch_res_pow != {}:
                    term_val = parser.parse(" {} * e ^ ({} * {} + {})".format(
                        copy(pmatch_res["A1"]) * copy(pmatch_res_pow["B1"]),
                        pmatch_res_pow["B1"],
                        self.wrt,
                        pmatch_res_pow.get("B2", 0)
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
