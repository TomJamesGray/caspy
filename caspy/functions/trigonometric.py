import logging
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg
from caspy.pattern_match import pmatch,pat_construct
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol

logger = logging.getLogger(__name__)

class TrigFunc(Function1Arg):
    pass


class Sin(TrigFunc):
    fname = "sin"
    latex_fname = "\\sin"
    pi_coeffs = [
        [Fraction(1,2),"1"],
        [Fraction(1,3),"3^(1/2)/2"],
        [Fraction(1,4),"2^(-1/2)"],
        [Fraction(1,6),"1/2"],
        [Fraction(1,1),"0"]
    ]

    def __init__(self,x):
        self.arg = x
        super().__init__()

    def eval(self):
        pat = pat_construct("a*pi",{"a":"const"})
        pmatch_res = pmatch(pat,self.arg)
        a_val = pmatch_res["a"]
        if pmatch_res != {}:
            # Don't check against a_val as 0 == False
            for (coeff,val) in self.pi_coeffs:
                if coeff == a_val:
                    return self.parser.parse(val)

        return Numeric(Symbol(self,Fraction(1,1)),"sym_obj")
