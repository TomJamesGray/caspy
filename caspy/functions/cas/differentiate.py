import logging
from copy import copy,deepcopy
import caspy.numeric.numeric
import caspy.pattern_match as pm
import caspy.parsing.parser
import caspy.functions.trigonometric as trig
import caspy.functions.cas.expand as expand
from caspy.functions.function import Function
from caspy.printing import latex_numeric as ln
from caspy.helpers.helpers import group_list_into_all_poss_pairs

logger = logging.getLogger(__name__)


class Differentiate(Function):
    """Caspy function to differentiate a numeric object symbolically"""
    fname = "diff"

    def __init__(self, arg, wrt="x", root_diff=True,dont_expand=False):
        self.arg = arg
        self.fully_diffed = False
        self.root_diff = root_diff
        self.parser = caspy.parsing.parser.Parser()
        self.dont_expand = dont_expand
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
                                       {"n": "const", "a": "const"}, sym, self.parser)
            if pmatch_res != {}:
                term_val = self.parser.parse("{} * {} ^ ({})".format(
                    copy(pmatch_res["a"]) * copy(pmatch_res["n"]),
                    self.wrt,
                    copy(pmatch_res["n"]) - 1
                ))
                tot += term_val
                diffed_values.append(i)
                continue

            # Try diffing sin terms
            pmatch_res = pm.pmatch_sym("A1*sin(A2)",
                                       {"A1": "const", "A2": "rem"}, sym, self.parser)
            if pmatch_res != {}:
                logger.debug("Differentiating sin term")
                # Diff the argument
                d_obj = Differentiate(pmatch_res["A2"],self.wrt)
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
                                       {"A1": "const", "A2": "rem"}, sym, self.parser)
            if pmatch_res != {}:
                logger.debug("Differentiating cos term")
                # Diff the argument
                d_obj = Differentiate(pmatch_res["A2"],self.wrt)
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
                                       {"A1": "const", "A2": "rem"}, sym, self.parser)
            if pmatch_res != {}:
                logger.debug("Differentiating ln term")
                # Diff the argument
                d_obj = Differentiate(deepcopy(pmatch_res["A2"]),self.wrt)
                derivative = d_obj.eval()
                if d_obj.fully_diffed:
                    derivative.simplify()
                    numeric_coeff = caspy.numeric.numeric.Numeric(
                        pmatch_res["A1"], "number"
                    )
                    term_val = numeric_coeff * derivative / deepcopy(pmatch_res["A2"])
                    tot += term_val
                    diffed_values.append(i)
                    continue

            # Try differentiating exponential terms
            pmatch_res = pm.pmatch_sym("A1 * e^(A2)".format(self.wrt),
                                    {"A1": "const", "A2": "rem"}, sym, self.parser)
            if pmatch_res != {}:
                logger.debug("Differentiating exponential term, pmatch result {}".format(pmatch_res))
                # Currently pattern matching doesn't quite work correctly with matching
                # things like e^(a*x+b) so we will have to pattern match the A2 term
                exp_pow = expand.Expand(deepcopy(pmatch_res["A2"])).eval()
                d_obj = Differentiate(exp_pow, self.wrt)
                derivative = d_obj.eval()
                if d_obj.fully_diffed:
                    derivative.simplify()
                    term_val = caspy.numeric.numeric.Numeric(copy(pmatch_res["A1"]))
                    term_val.val[0].val.append(["e",pmatch_res["A2"]])
                    term_val *= derivative
                    tot += term_val
                    diffed_values.append(i)
                    continue

            if self.root_diff and not self.dont_expand:
                sym_numeric = caspy.numeric.numeric.Numeric(deepcopy(sym), "sym_obj")
                expand_obj = expand.Expand(sym_numeric)
                expanded = expand_obj.eval()
                logger.critical("Expanded val: {}".format(ln.latex_numeric_str(expanded)))
                diff_exp = Differentiate(expanded, self.wrt, True, True)
                new_integral = diff_exp.eval()
                if diff_exp.fully_diffed:
                    diffed_values.append(i)
                    tot += new_integral
                    continue
                else:
                    logger.critical("Failed expanded diff {}".format(ln.latex_numeric_str(new_integral)))

            if not self.root_diff:
                continue
            diffed_by_parts = False
            # Try differentiation of products
            for (a,b) in group_list_into_all_poss_pairs(deepcopy(sym.val)):
                derivatives = []
                non_derivatives = []
                diff_prod_pair_fail = False
                for part in [a,b]:
                    # Generate numeric objects for it
                    part_num = caspy.numeric.numeric.Numeric(0)
                    part_num.val[0].val = deepcopy(part)
                    part_diff_obj = Differentiate(part_num,self.wrt,False)
                    part_derivative = part_diff_obj.eval()
                    if part_diff_obj.fully_diffed:
                        derivatives.append(part_derivative.simplify())
                        non_derivatives.append(part_num)
                    else:
                        diff_prod_pair_fail = True
                        break
                if diff_prod_pair_fail:
                    continue
                # We have differentiaed the products
                term_val = deepcopy(derivatives[0]) * deepcopy(non_derivatives[1]) + \
                           deepcopy(derivatives[1]) * deepcopy(non_derivatives[0])
                tot += term_val
                diffed_values.append(i)
                diffed_by_parts = True
                break
            if diffed_by_parts:
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
