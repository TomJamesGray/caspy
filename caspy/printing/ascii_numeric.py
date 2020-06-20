from caspy.numeric.numeric import Num


def ascii_numeric_str(x: Num):
    out = ""
    for sym in x.val:
        out += "({}) ".format(sym.coeff)
        for key in sym.val:
            if key != 1:
                out += "* {} ^ (".format(key)
                out += ascii_numeric_str(sym.val[key])
                out += ")"
        out += " + "
    return out[:-3]