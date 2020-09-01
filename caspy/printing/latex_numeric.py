import caspy.numeric.numeric as num
from caspy.functions import function as fn
from caspy.numeric.fraction import to_int
from caspy.numeric.fraction import Fraction


def latex_numeric_str(x):
    if type(x) != num.Numeric:
        return str(x)
    out = ""
    for sym in x.val:
        need_dot = False
        sym.simplify()
        if sym.val == [[-1,1]]:
            # Handles case when the symbol is just the number '-1' on it's own
            out += "-1"
        elif not (sym.coeff.num == 1 and sym.coeff.den == 1):
            need_dot = True
            # Print the coefficient as a fraction only if necessary
            if sym.coeff.num == 0:
                # Include the '+' so it doesn't get chopped off by return out[:-1]
                out += "0+"
                continue
            elif sym.coeff.num == -1 and sym.coeff.den == 1:
                out += "-"
                need_dot = False
            elif sym.coeff.den == 1:
                out += "{}".format(to_int(sym.coeff.num))
            elif sym.coeff.den == -1:
                out += "{}".format(to_int(sym.coeff.num * -1))
            else:
                out += "\\frac{{{}}}{{{}}}".format(to_int(sym.coeff.num), to_int(sym.coeff.den))
        elif sym.val == [[1,1]]:
            # Handles case when the symbol is just the number '1' on it's own
            out += "{}".format(to_int(sym.coeff.num))

        i = -1
        for (sym_name,pow) in sym.val:
            i += 1
            if sym_name != 1 and i != sym.get_coeff_index():
                if need_dot:
                    out += "\\cdot"
                    need_dot = False
                if type(sym_name) == num.Numeric:
                    power = latex_numeric_str(sym_name)
                    if power != "" and power != "1":
                        out += "({})".format(power)
                elif isinstance(sym_name, fn.Function):
                    out += sym_name.latex_format()
                else:
                    out += " {}".format(sym_name)
                power = latex_numeric_str(pow)
                if power != "" and power != "1":
                    out += "^ {{{}}}".format(power)
            elif type(pow) == num.Numeric:
                out += "^ {{{}}}".format(latex_numeric_str(pow))

        out += "+"
    return out[:-1]
