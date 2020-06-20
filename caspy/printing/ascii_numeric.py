from caspy.numeric.numeric import Num,Numeric


def ascii_numeric_str(x: Num):
    out = ""
    for sym in x.val:
        out += "({}) ".format(sym.coeff)
        for key in sym.val:
            if key != 1:
                if type(key) == Numeric:
                    out += "* ({}) ^ (".format(ascii_numeric_str(key))
                else:
                    out += "* {} ^ (".format(key)
                out += ascii_numeric_str(sym.val[key])
                out += ")"
            elif type(sym.val[key]) == Numeric:
                out += "^ ({})".format(ascii_numeric_str(sym.val[key]))
        out += " + "
    return out[:-3]
