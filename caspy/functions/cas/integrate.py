import logging
from copy import copy,deepcopy
import caspy.numeric.numeric
import caspy.numeric.symbol
import caspy.pattern_match as pm
import caspy.parsing.parser
import caspy.functions.cas.differentiate as diff
import caspy.functions.cas.expand as expand
import caspy.functions.trigonometric as trig
from caspy.functions.function import Function
from caspy.printing import latex_numeric as ln
from caspy.helpers.helpers import group_list_into_all_poss_pairs
from caspy.numeric.fraction import Fraction

logger = logging.getLogger(__name__)


def pmatch_sym(pat, pat_dict, sym):
    pat = pm.pat_construct(pat, pat_dict)
    numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
    pmatch_res, _ = pm.pmatch(pat, numeric_wrapper)
    return pmatch_res


class Integrate(Function):
    """Caspy function to integrate a numeric object symbolically"""
    fname = "integrate"
    latex_fname = "integrate"

    def __init__(self, arg, wrt="x", root_integral=True):
        self.arg = arg
        self.fully_integrated = False
        self.root_integral = root_integral
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
        return "\\int {} \\mathrm{{d}}{}".format(ln.latex_numeric_str(self.arg),self.wrt)

    def u_sub_int(self, u, integrand):
        """
        Tries to integrate a symbol using a u substitution
        :param u: substitution to make - Numeric object
        :param integrand: numeric object to integrate
        :return: Numeric object
        """
        diff_obj = diff.Differentiate(u,self.wrt)
        derivative = diff_obj.eval()
        if diff_obj.fully_diffed:
            derivative.simplify()
            new_val = integrand / derivative
            new_val.simplify()
            logger.warning("New val is {}".format(new_val))
            # Need to try and replace the occurrences of u in terms of with
            # respect to self.wrt with another variable. So if u = x^2 then
            # sin(x^2) --> sin(u)
            var_obj = caspy.numeric.numeric.Numeric("U1","sym")
            logger.warning("Replacing with {}".format(var_obj))

            replaced_obj = new_val.try_replace_numeric_with_var(u,var_obj)
            logger.warning("Replaced obj is {}".format(replaced_obj))
            if replaced_obj is not None:
                # Try and integrate replaced_obj wrt to u
                subbed_int = Integrate(replaced_obj,"U1", False)
                int_result = subbed_int.eval()
                if subbed_int.fully_integrated:
                    return int_result.try_replace_numeric_with_var(var_obj,u)
        return None

    def int_by_parts(self, u_prime, v):
        """
        Tries to integrate a symbol by parts by splitting the symbol into
        2 parts u_prime and v. So
        integral(u_prime * v) = u * v - integral(u * diff(v))
        where u = integral(u_prime)
        :param u_prime: Numeric object
        :param v: Numeric object
        :return: Numeric object
        """
        # Make it not root integral so we don't get lots of recursion
        int_u_obj = Integrate(u_prime,self.wrt,False)
        u = int_u_obj.eval()
        if not int_u_obj.fully_integrated:
            return None

        diff_v_obj = diff.Differentiate(v,self.wrt)
        v_prime = diff_v_obj.eval()
        if not diff_v_obj.fully_diffed:
            return None
        logger.debug("Int by parts u: {}, v_prime: {}".format(
            ln.latex_numeric_str(u),
            ln.latex_numeric_str(v_prime)
        ))
        part_to_int = deepcopy(u) * deepcopy(v_prime)
        # Make it not root integral so we don't get lots of recursion
        int_part_obj = Integrate(part_to_int,self.wrt, False)
        int_part_val = int_part_obj.eval()
        if not int_part_obj.fully_integrated:
            return None

        return deepcopy(u) * deepcopy(v) - deepcopy(int_part_val)

    def eval(self):
        """
        Evaluates the integral. This will be done symbol by symbol, so for
        instance 2*x^2 + sin(x) will be done by integrating 2x^2 then sin(x)
        :return: Numeric object
        """
        logger.debug("Attempting to integrate {}".format(self.arg))
        parser = caspy.parsing.parser.Parser()
        tot = caspy.numeric.numeric.Numeric(0,"number")
        integrated_values = []
        for i,sym in enumerate(self.arg.val):
            # Simplify symbol, this get's rid of issues caused by terms
            # like x^0
            sym.simplify()
            if sym.is_exclusive_numeric():
                # Integrate constant term
                frac_val = sym.sym_frac_eval()
                frac_val_num = caspy.numeric.numeric.Numeric(frac_val, "number")
                wrt_term = caspy.numeric.numeric.Numeric(self.wrt, "sym")
                tot += wrt_term * frac_val_num
                integrated_values.append(i)
                # Go onto next term
                continue

            if not sym.has_variable_in(self.wrt):
                # Integrate term that doesn't contain the variable we're
                # integrating with respect to
                sym_numeric_obj = caspy.numeric.numeric.Numeric(sym,"sym_obj")
                wrt_term = caspy.numeric.numeric.Numeric(self.wrt, "sym")
                tot += sym_numeric_obj * wrt_term
                integrated_values.append(i)
                continue

            # Try matching x^n
            pmatch_res = pm.pmatch_sym("a*{}^n".format(self.wrt),
                                    {"n":"const","a":"const"}, sym)
            if pmatch_res != {}:
                logger.debug("Integrating polynomial term {}, pmatch result {}".format(sym,pmatch_res))
                if pmatch_res["n"] == -1:
                    term_val = parser.parse("{} * ln({})".format(
                        copy(pmatch_res["a"]), self.wrt
                    ))
                else:
                    # TODO maybe refactor Fraction class so it doesn't return self
                    # so we don't need to do a ridiculous amount of copying like this
                    term_val = parser.parse("{} * {} ^ ({})".format(
                        copy(pmatch_res["a"])/(copy(pmatch_res["n"])+1), self.wrt, copy(pmatch_res["n"]) + 1
                    ))
                tot += term_val
                integrated_values.append(i)
                # Go onto next term
                continue

            # Try integrating exponential terms
            pmatch_res = pm.pmatch_sym("A1 * e^(A2)".format(self.wrt),
                                    {"A1": "const", "A2": "rem"}, sym)
            if pmatch_res != {}:
                logger.debug("Integrating exponential term, pmatch result {}".format(pmatch_res))
                # Currently pattern matching doesn't quite work correctly with matching
                # things like e^(a*x+b) so we will have to pattern match the A2 term
                exp_pow = expand.Expand(pmatch_res["A2"]).eval()
                pat = pm.pat_construct("B1 * {} + B2".format(self.wrt),
                                       {"B1": "const", "B2": "rem"})
                pmatch_res_pow, _ = pm.pmatch(pat,exp_pow)
                logger.debug("Power pmatch result {}".format(pmatch_res_pow))
                if "B1" in pmatch_res_pow.keys():
                    failed_int = False
                    if "B2" in pmatch_res_pow.keys():
                        if self.wrt in pmatch_res_pow["B2"].get_variables_in():
                            logger.debug("Failed integration of exponential term")
                            failed_int = True
                    if not failed_int:
                        term_val = caspy.numeric.numeric.Numeric(
                            copy(pmatch_res["A1"]) / copy(pmatch_res_pow["B1"])
                        )
                        term_val.val[0].val.append(["e",deepcopy(pmatch_res["A2"])])
                        tot += term_val
                        integrated_values.append(i)
                        continue

            # Try matching simple sin terms like sin(ax+b)
            pmatch_res = pm.pmatch_sym("a*sin(b*{}+c)".format(self.wrt),
                                    {"a": "const", "b": "const", "c": "const"},
                                    sym)
            if pmatch_res != {}:
                logger.debug("Integrating simple linear sin term")
                term_val = parser.parse("{} * cos({}*{}+{})".format(
                    copy(pmatch_res["a"])*(-1)/copy(pmatch_res["b"]), pmatch_res["b"],
                    self.wrt, pmatch_res.get("c",0)
                ))
                tot += term_val
                integrated_values.append(i)
                continue

            # Try matching simple sin terms like cos(ax+b)
            pmatch_res = pm.pmatch_sym("a*cos(b*{}+c)".format(self.wrt),
                                    {"a": "const", "b": "const", "c": "const"},
                                    sym)
            if pmatch_res != {}:
                logger.debug("Integrating simple linear cos term")
                term_val = parser.parse("{} * sin({}*{}+{})".format(
                    copy(pmatch_res["a"]) / copy(pmatch_res["b"]), pmatch_res["b"],
                    self.wrt, pmatch_res.get("c", 0)
                ))
                tot += term_val
                integrated_values.append(i)
                continue

            # Try integrating sin(___) term with a 'u' substitution
            pmatch_res = pm.pmatch_sym("b*sin(a)", {"a": "rem","b":"coeff"}, sym)
            if pmatch_res != {}:
                logger.debug("Integrating sin object with u sub, pmatch_res {}".format(pmatch_res))
                numeric_wrapper = caspy.numeric.numeric.Numeric(deepcopy(sym), "sym_obj")
                u_subbed = self.u_sub_int(pmatch_res["a"],numeric_wrapper)
                if u_subbed is not None:
                    logger.warning("U sub integral worked")
                    tot += u_subbed
                    integrated_values.append(i)
                    continue

            # Try integrating cos(___) term with a 'u' substitution
            pmatch_res = pm.pmatch_sym("b*cos(a)", {"a": "rem", "b": "coeff"}, sym)
            if pmatch_res != {}:
                logger.debug("Integrating cos object with u sub, pmatch_res {}".format(pmatch_res))
                numeric_wrapper = caspy.numeric.numeric.Numeric(deepcopy(sym), "sym_obj")
                u_subbed = self.u_sub_int(pmatch_res["a"], numeric_wrapper)
                if u_subbed is not None:
                    logger.warning("U sub integral worked")
                    tot += u_subbed
                    integrated_values.append(i)
                    continue

            if self.root_integral:
                # Try expanding the symbol then integrating
                sym_numeric = caspy.numeric.numeric.Numeric(deepcopy(sym),"sym_obj")
                expand_obj = expand.Expand(sym_numeric)
                expanded = expand_obj.eval()
                integ_exp = Integrate(expanded,self.wrt,False)
                new_integral = integ_exp.eval()
                if integ_exp.fully_integrated:
                    integrated_values.append(i)
                    tot += new_integral
                    continue

            if not self.root_integral:
                continue
            # Try integrating by parts
            int_done_by_parts = False
            for (a,b) in group_list_into_all_poss_pairs(deepcopy(sym.val)):
                # Make symbols for a and b\
                a_sym = caspy.numeric.symbol.Symbol(1,Fraction(1,1))
                a_sym.val = a
                a_num = caspy.numeric.numeric.Numeric(a_sym,"sym_obj")
                b_sym = caspy.numeric.symbol.Symbol(1, Fraction(1, 1))
                b_sym.val = b
                b_num = caspy.numeric.numeric.Numeric(b_sym,"sym_obj")
                logger.debug("PRE Int by parts u_prime {} v {}".format(
                    ln.latex_numeric_str(a_num),
                    ln.latex_numeric_str(b_num)))
                by_parts_ab = self.int_by_parts(a_num,b_num)
                if by_parts_ab is not None:
                    logger.debug("Int by parts u_prime {} v {}".format(
                        ln.latex_numeric_str(a_num),
                        ln.latex_numeric_str(b_num)))
                    tot += by_parts_ab
                    integrated_values.append(i)
                    int_done_by_parts = True
                else:
                    by_part_ba = self.int_by_parts(b_num,a_num)
                    if by_part_ba is not None:
                        logger.debug("Int by parts2 u_prime {} v {}".format(
                            ln.latex_numeric_str(b_num),
                            ln.latex_numeric_str(a_num)))
                        tot += by_part_ba
                        integrated_values.append(i)
                        int_done_by_parts = True

                if int_done_by_parts:
                    break
                else:
                    logger.debug("One round of int by parts failed")

            if int_done_by_parts:
                continue


        new_val = []
        # Remove integrated values from the arg property
        for j,term_val in enumerate(self.arg.val):
            if j not in integrated_values:
                new_val.append(term_val)

        if new_val == []:
            # All terms have been integrated
            self.fully_integrated = True
            return tot
        else:
            # Make a numeric object to store the non integrated terms
            new_val_numeric_obj = caspy.numeric.numeric.Numeric(1,"number")
            new_val_numeric_obj.val = new_val
            self.arg = new_val_numeric_obj
            # Return integrated terms and other terms in an integral
            remaining_int = super().eval()
            return remaining_int + tot
