import logging
from copy import copy
import caspy.numeric.numeric
import caspy.pattern_match as pm
import caspy.parsing.parser
from caspy.functions.function import Function
from caspy.printing import latex_numeric as ln

logger = logging.getLogger(__name__)


class Integrate(Function):
    """Function to integrate a numeric object symbolically"""
    fname = "integrate"
    latex_fname = "integrate"

    def __init__(self, arg, wrt="x"):
        self.arg = arg
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


        new_val = []
        # Remove integrated values from the arg property
        for j,term_val in enumerate(self.arg.val):
            if j not in integrated_values:
                new_val.append(term_val)

        if new_val == []:
            # All terms have been integrated
            return tot
        else:
            # Make a numeric object to store the non integrated terms
            new_val_numeric_obj = caspy.numeric.numeric.Numeric(1,"number")
            new_val_numeric_obj.val = new_val
            self.arg = new_val_numeric_obj
            # Return integrated terms and other terms in an integral
            remaining_int = super().eval()
            return remaining_int + tot
