import logging
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg
from caspy.pattern_match import pmatch, pat_construct
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol

logger = logging.getLogger(__name__)


class TrigFunc(Function1Arg):
    def shift_to_2pi(self, x: Fraction):
        """
        Takes a fraction that represents a coefficient of pi and shifts it
        so it lies in the range 0 to 2
        :param x: Fraction
        :return: Fraction
        """
        if x > Fraction(0, 1):
            while x > Fraction(2, 1):
                x -= 2
        elif x < Fraction(0, 1):
            while x < Fraction(2, 1):
                x += 2

        return x


class Sin(TrigFunc):
    fname = "sin"
    latex_fname = "\\sin"

    set_points = []

    def __init__(self, x):
        self.pi_coeffs = [
            [Fraction(1, 2), "1"],
            [Fraction(1, 3), "3^(1/2)/2"],
            [Fraction(2, 3), "3^(1/2)/2"],
            [Fraction(1, 4), "2^(-1/2)"],
            [Fraction(3, 4), "2^(-1/2)"],
            [Fraction(1, 6), "1/2"],
            [Fraction(5, 6), "1/2"],
            [Fraction(1, 1), "0"]
        ]
        self.arg = x
        super().__init__()

    def eval(self):
        pat = pat_construct("a*pi", {"a": "const"})
        pmatch_res = pmatch(pat, self.arg)
        if pmatch_res != {}:
            # Don't check against a_val as 0 == False
            a_val = pmatch_res["a"]
            a_val = self.shift_to_2pi(a_val)
            logger.debug("a_val is {}".format(a_val))
            neg = False

            if a_val > Fraction(1, 1):
                # If a is between 1 and 2 we can work out -sin((a-1)*pi)
                # to get the same result
                neg = True
                a_val -= 1

            fnd = False
            for (coeff, val) in self.pi_coeffs:
                if coeff == a_val:
                    fnd = True
                    numeric_val = self.parser.parse(val)
                    break
            if fnd:
                if neg:
                    return numeric_val.neg()
                else:
                    return numeric_val

        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")


class Cos(TrigFunc):
    fname = "cos"
    latex_fname = "\\cos"
    set_points = []

    def __init__(self,x):
        self.arg = x
        super().__init__()

    def eval(self):
        pat = pat_construct("a*pi", {"a": "const"})
        pmatch_res = pmatch(pat, self.arg)
        if pmatch_res != {}:
            # Don't check against a_val as 0 == False
            a_val = pmatch_res["a"]
            # Try and use sin to evaluate this as
            # cos(x) = sin(x+pi/2)
            sin_a_val = a_val + Fraction(1, 2)
            sin_val = Sin(self.parser.parse("pi * {}".format(sin_a_val))).eval()
            if sin_val.is_exclusive_numeric():
                return sin_val

        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")
