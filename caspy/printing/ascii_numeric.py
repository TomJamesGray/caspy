from caspy.numeric.numeric import Numeric
from caspy.functions.function import Function1Arg


def ascii_numeric_str(x):
    if type(x) != Numeric:
        return str(x)
    out = ""
    for sym in x.val:
        out += "({}) ".format(sym.coeff)
        for (sym_name,pow) in sym.val:
            if sym_name != 1:
                if type(sym_name) == Numeric:
                    out += "* ({}) ^ (".format(ascii_numeric_str(sym_name))
                elif isinstance(sym_name,Function1Arg):
                    out += "* {}({}) ^ (".format(sym_name.fname,ascii_numeric_str(sym_name.arg))
                else:
                    out += "* {} ^ (".format(sym_name)
                out += ascii_numeric_str(pow)
                out += ")"
            elif type(pow) == Numeric:
                out += "^ ({})".format(ascii_numeric_str(pow))
        out += " + "
    return out[:-3]
