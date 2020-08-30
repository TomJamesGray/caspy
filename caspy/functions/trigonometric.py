import logging
import math
import caspy.pattern_match
import caspy.parsing.parser
from caspy.numeric.fraction import Fraction
from caspy.functions.function import Function1Arg
from caspy.numeric.numeric import Numeric
from caspy.numeric.symbol import Symbol

logger = logging.getLogger(__name__)


class TrigFunc(Function1Arg):
    def __init__(self):
        self.parser = caspy.parsing.parser.Parser()
        super().__init__()

    def shift_to_2pi(self, x: Fraction):
        """
        Takes a fraction that represents a coefficient of pi and shifts it
        so it lies in the range 0 to 2
        :param x: Fraction
        :return: Fraction
        """
        if x.to_real() > 0:
            if int(x.to_real()) % 2 == 0:
                x -= int(x.to_real())
            else:
                x = x - int(x.to_real()) + 1
        else:
            if (int(x.to_real())-1) % 2 == 0:
                x -= int(x.to_real()) - 1
            else:
                x = x - (int(x.to_real())-1) + 1
        return x


class Sin(TrigFunc):
    fname = "sin"
    latex_fname = "\\sin"

    def __init__(self, x):
        self.pi_coeffs = [
            [Fraction(1, 2), "1"],
            [Fraction(1, 3), "sqrt(3)/2"],
            [Fraction(2, 3), "sqrt(3)/2"],
            [Fraction(1, 4), "sqrt(1/2)"],
            [Fraction(3, 4), "sqrt(1/2)"],
            [Fraction(1, 6), "1/2"],
            [Fraction(5, 6), "1/2"],
            [Fraction(1, 1), "0"],
            [Fraction(0, 1), "0"]
        ]
        self.arg = x
        super().__init__()

    def to_frac(self):
        if self.arg.is_exclusive_numeric():
            return Fraction(math.sin(self.arg.frac_eval().to_real()), 1)
        else:
            logger.error("Argument {} of sqrt isn't exclusive numeric".format(
                self.arg
            ))

    def eval(self):
        pat = caspy.pattern_match.pat_construct("a*pi", {"a": "const"})
        pmatch_res, _ = caspy.pattern_match.pmatch(pat, self.arg)
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
        elif self.arg == Numeric(0,"number"):
            # TODO somehow add handling for case a=0 in pattern matching
            return Numeric(0,"number")
        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")


class Cos(TrigFunc):
    fname = "cos"
    latex_fname = "\\cos"

    def __init__(self,x):
        self.arg = x
        super().__init__()

    def to_frac(self):
        if self.arg.is_exclusive_numeric():
            return Fraction(math.cos(self.arg.frac_eval().to_real()), 1)
        else:
            logger.error("Argument {} of sqrt isn't exclusive numeric".format(
                self.arg
            ))

    def eval(self):
        pat = caspy.pattern_match.pat_construct("a*pi", {"a": "const"})
        pmatch_res, _ = caspy.pattern_match.pmatch(pat, self.arg)
        if pmatch_res != {}:
            # Don't check against a_val as 0 == False
            a_val = pmatch_res["a"]
            # Try and use sin to evaluate this as
            # cos(x) = sin(x+pi/2)
            sin_a_val = a_val + Fraction(1, 2)
            sin_val = Sin(self.parser.parse("pi * {}".format(sin_a_val))).eval()
            if sin_val.is_exclusive_numeric():
                return sin_val
        elif self.arg == Numeric(0,"number"):
            # TODO somehow add handling for case a=0 in pattern matching
            return Numeric(1,"number")
        return Numeric(Symbol(self, Fraction(1, 1)), "sym_obj")


class Tan(TrigFunc):
    fname = "tan"
    latex_fname = "\\tan"

    def __init__(self, x):
        self.arg = x
        super().__init__()

    def to_frac(self):
        if self.arg.is_exclusive_numeric():
            return Fraction(math.tan(self.arg.frac_eval().to_real()), 1)
        else:
            logger.error("Argument {} of sqrt isn't exclusive numeric".format(
                self.arg
            ))

    def eval(self):
        """Evaluates the tan function by computing sin(x)/cos(x)"""
        pat = caspy.pattern_match.pat_construct("A1*pi", {"A1": "const"})
        pmatch_res, _ = caspy.pattern_match.pmatch(pat, self.arg)
        if pmatch_res != {}:
            sin_x = Sin(self.arg).eval()
            cos_x = Cos(self.arg).eval()
            # TODO make it so that 1/sqrt(3) automatically simplifies to sqrt(3)/3
            if sin_x.is_exclusive_numeric() and cos_x.is_exclusive_numeric():
                return sin_x / cos_x

        return super().eval()
