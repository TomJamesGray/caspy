import logging
from copy import copy
import caspy.numeric.numeric
import caspy.numeric.symbol
import caspy.pattern_match as pm
import caspy.parsing.parser
import caspy.functions.cas.differentiate as diff
import caspy.functions.trigonometric as trig
from caspy.functions.function import Function
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Integrate(Function):
    """Caspy function to integrate a numeric object symbolically"""
    fname = "integrate"
    latex_fname = "integrate"

    def __init__(self, arg, wrt="x"):
        self.arg = arg
        self.fully_integrated = False
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
        Try's to integrate a symbol using a u substitution
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
            var_obj = caspy.numeric.numeric.Numeric(u,"sym")
            logger.warning("Replacing with {}".format(var_obj))

            replaced_obj = new_val.try_replace_numeric_with_var(var_obj,"u")
            logger.warning("Replaced obj is {}".format(replaced_obj))
            if replaced_obj is not None:
                # Try and integrate replaced_obj wrt to u
                subbed_int = Integrate(replaced_obj,"u")
                int_result = subbed_int.eval()
                if subbed_int.fully_integrated:
                    return int_result
        return None

    def eval(self):
        """
        Evaluates the integral. This will be done symbol by symbol, so for
        instance 2*x^2 + sin(x) will be done by integrating 2x^2 then sin(x)
        :return: Numeirc object
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
            pat = pm.pat_construct("a*{}^n".format(self.wrt),{"n":"const","a":"const"})
            numeric_wrapper = caspy.numeric.numeric.Numeric(sym,"sym_obj")
            pmatch_res,_ = pm.pmatch(pat,numeric_wrapper)
            if pmatch_res != {}:
                logger.debug("Integrating polynomial term {}, pmatch result {}".format(sym,pmatch_res))
                if pmatch_res["n"] == -1:
                    term_val = parser.parse("{} * ln({})".format(
                        copy(pmatch_res["a"]), self.wrt
                    ))
                else:
                    # TODO maybe refactor Fraction class so it doesn't return self
                    # so we don't need to do a ridiculous amount of copying like this
                    term_val = parser.parse("{} * {} ^ {}".format(
                        copy(pmatch_res["a"])/(copy(pmatch_res["n"])+1), self.wrt, copy(pmatch_res["n"]) + 1
                    ))
                tot += term_val
                integrated_values.append(i)
                # Go onto next term
                continue

            # Try matching simple sin terms like sin(ax+b)
            pat = pm.pat_construct("a*sin(b*{}+c)".format(self.wrt),
                                   {"a": "const", "b": "const", "c": "const"})
            numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
            pmatch_res, _ = pm.pmatch(pat, numeric_wrapper)
            if pmatch_res != {}:
                logger.debug("Integrating simple linear sin term")
                term_val = parser.parse("{} * cos({}*{}+{})".format(
                    copy(pmatch_res["a"])*(-1)/copy(pmatch_res["b"]), pmatch_res["b"],
                    self.wrt, pmatch_res.get("c",0)
                ))
                tot += term_val
                integrated_values.append(i)
                continue

            # Try integrating sin(___) term with a 'u' substitution
            pat = pm.pat_construct("b*sin(a)", {"a": "rem","b":"coeff"})
            numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
            pmatch_res, _ = pm.pmatch(pat, numeric_wrapper)
            if pmatch_res != {}:
                logger.warning("Integrating sin object with u sub, pmatch_res {}".format(pmatch_res))

                u_subbed = self.u_sub_int(pmatch_res["a"],numeric_wrapper)
                if u_subbed is not None:
                    logger.warning("U sub integral worked")
                    tot += u_subbed
                    integrated_values.append(i)
                    continue

            # Try integrating cos(___) term with a 'u' substitution
            pat = pm.pat_construct("b*cos(a)", {"a": "rem", "b": "coeff"})
            numeric_wrapper = caspy.numeric.numeric.Numeric(sym, "sym_obj")
            pmatch_res, _ = pm.pmatch(pat, numeric_wrapper)
            if pmatch_res != {}:
                logger.debug("Integrating sin object, pmatch_res {}".format(pmatch_res))
                # Differentiate the argument of sin
                diff_obj = diff.Differentiate(pmatch_res["a"])
                derivative = diff_obj.eval()
                if diff_obj.fully_diffed:
                    derivative.simplify()
                    val_coeff = pmatch_res["b"] / derivative
                    val_coeff.simplify()
                    if val_coeff.is_exclusive_numeric():
                        term_val = caspy.numeric.numeric.Numeric(
                            val_coeff.frac_eval(), "number"
                        )
                        # Multiply cos(a) onto the numeric object by appending
                        # it to the symbol
                        cos_obj = trig.Sin(pmatch_res["a"])
                        term_val.val[0].val.append([
                            cos_obj, 1
                        ])
                        integrated_values.append(i)
                        tot += term_val
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
