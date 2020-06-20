from caspy.numeric.numeric import Num,Numeric


def to_int(x: float):
    """Casts x to integer if it doesn't change the value"""
    if x == int(x):
        return int(x)
    else:
        return x


def latex_numeric_str(x: Num):
    out = ""
    for sym in x.val:
        need_dot = False
        if not(sym.coeff.num == 1 and sym.coeff.den == 1):
            need_dot = True
            # Print the coefficient as a fraction only if necessary
            if sym.coeff.den == 1:
                out += "{}".format(to_int(sym.coeff.num))
            else:
                out += "\\frac{{{}}}{{{}}}".format(to_int(sym.coeff.num), to_int(sym.coeff.den))
        elif sym.val == {1: 1}:
            # Handles case when the symbol is just the number '1' on it's own
            out += "{}".format(to_int(sym.coeff.num))

        for key in sym.val:
            if key != 1:
                if need_dot:
                    out += "\\cdot"
                    need_dot = False
                if type(key) == Numeric:
                    power = latex_numeric_str(key)
                    if power != "" and power != "1":
                        out += "({})".format(power)

                else:
                    out += " {}".format(key)
                power = latex_numeric_str(sym.val[key])
                if power != "" and power != "1":
                    out += "^ {{{}}}".format(power)
            elif type(sym.val[key]) == Numeric:
                out += "^ {{{}}}".format(latex_numeric_str(sym.val[key]))

        out += "+"
    return out[:-1]
