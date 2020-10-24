import caspy.numeric.numeric as num
from caspy.functions import function as fn
from caspy.numeric.fraction import to_int
from caspy.numeric.fraction import Fraction


def latex_numeric_str(x):
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
                out += "\\frac{{{}}}{{{}}}".format(
                    abs(to_int(sym.coeff.num)), abs(to_int(sym.coeff.den)))

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
                    print("Recursing for {}".format(sym_name))
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
        if sym_pos + 1 < len(x.val):
            # Check we aren't on the last term
            if x.val[sym_pos + 1].coeff.to_real() < 0:
                out += "-"
            else:
                out += "+"

        # out += "+"
    return out
