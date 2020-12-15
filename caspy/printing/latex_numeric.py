import logging
import caspy.numeric.numeric as num
from caspy.functions import function as fn
from caspy.numeric.fraction import to_int
from caspy.numeric.fraction import Fraction


logger = logging.getLogger(__name__)


def latex_numeric_str(x,form="latex"):
    """
    Generates output string for x. Can give output in LaTeX or in ASCII
    :param x: Numeric object
    :param form: String, either `latex` or `ascii` or `unicode`
    :return: string
    """
    if form not in ("latex","ascii","unicode"):
        logger.error("Unrecognised form for output string {}".format(form))
    if type(x) != num.Numeric:
        return str(x)
    out = ""
    for sym_pos,sym in enumerate(x.val):
        need_dot = False
        sym.simplify()
        if sym.val == [[-1,1]]:
            # Handles case when the symbol is just the number '-1' on it's own
            if sym_pos == 0:
                out += "-1"
            else:
                out += "1"
        elif sym.coeff.num == -1 and sym.coeff.den == 1:
            if sym_pos == 0:
                out += "-"
                need_dot = False

        elif not (sym.coeff.num == 1 and sym.coeff.den == 1):
            need_dot = True
            if sym_pos == 0 and sym.coeff.to_real() < 0:
                out += "-"
            # Print the coefficient as a fraction only if necessary
            if sym.coeff.num == 0:
                out += "0"
                continue
            elif sym.coeff.den == 1:
                out += "{}".format(abs(to_int(sym.coeff.num)))
            elif sym.coeff.den == -1:
                out += "{}".format(abs(to_int(sym.coeff.num * -1)))
            else:
                if form == "latex":
                    out += "\\frac{{{}}}{{{}}}".format(
                        abs(to_int(sym.coeff.num)), abs(to_int(sym.coeff.den)))
                elif form in ("ascii","unicode"):
                    out += "({}/{})".format(
                        abs(to_int(sym.coeff.num)), abs(to_int(sym.coeff.den)))

        elif sym.val == [[1,1]]:
            # Handles case when the symbol is just the number '1' on it's own
            out += "{}".format(to_int(sym.coeff.num))
        i = -1
        for (sym_name,pow) in sym.val:
            i += 1
            if sym_name != 1 and i != sym.get_coeff_index():
                if need_dot:
                    if form == "latex":
                        out += "\\cdot "
                    elif form == "unicode":
                        out += " · "
                    elif form == "ascii":
                        out += " * "
                    need_dot = False
                if type(sym_name) == num.Numeric:
                    # print("Recursing for {}".format(sym_name))
                    power = latex_numeric_str(sym_name,form)
                    if power != "" and power != "1":
                        out += "({})".format(power)
                elif isinstance(sym_name, fn.Function):
                    if form == "latex":
                        out += sym_name.latex_format()
                    elif form == "ascii":
                        out += " {}".format(sym_name.ascii_format())
                    elif form == "unicode":
                        out += " {}".format(sym_name.unicode_format())
                elif type(sym_name) == str:
                    if sym_name == "pi" and form != "ascii":
                        if form == "latex":
                            out += "\pi "
                        elif form == "unicode":
                            out += "π"
                    else:
                        out += "{}".format(sym_name)
                else:
                    # Handles cases like 2^x
                    out += "{}".format(sym_name)
                power = latex_numeric_str(pow,form)
                if power != "" and power != "1":
                    if form == "latex":
                        out += "^{{{}}}".format(power)
                    elif form == "ascii":
                        out += "^({})".format(power)
                    elif form == "unicode":
                        superscript_powers = ['⁰', '¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹']
                        try:
                            int_pow = int(power)
                            # Create representation of power integer with superscript chars
                            if int_pow < 0:
                                # There is a unicode superscript negative symbol
                                # but it doesn't look that good so it's not implemented
                                power_val = "^({})".format(power)
                            else:
                                power_val = ""
                                for char in str(abs(int_pow)):
                                    power_val += superscript_powers[int(char)]

                            out += power_val
                        except ValueError:
                            out += "^({})".format(power)

            elif type(pow) == num.Numeric:
                if form == "latex":
                    out += "^ {{{}}}".format(latex_numeric_str(pow,form))
                elif form in ("ascii","unicode"):
                    out += "^ ({})".format(latex_numeric_str(pow, form))
        if sym_pos + 1 < len(x.val):
            # Check we aren't on the last term
            if x.val[sym_pos + 1].coeff.to_real() < 0:
                out += " - "
            else:
                out += " + "

        # out += "+"
    return out
