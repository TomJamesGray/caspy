from typing import TypeVar,Generic
from caspy.factorise import factoriseNum
from collections import Counter

Frac = TypeVar("Frac")


def to_int(x: float):
    """Casts x to integer if it doesn't change the value"""
    if x == int(x):
        return int(x)
    else:
        return x


def product(ns: [int]) -> int:
    if ns == []:
        return 0
    val = 1
    for n in ns:
        val *= n
    return val


class Fraction(Generic[Frac]):
    """
    Represents a fraction
    """
    def __init__(self,num: float, den: float):
        self.num = num
        self.den = den
        self.simplify()

    def __repr__(self):
        if self.den == 1:
            return str(self.num)
        else:
            return "{}/{}".format(self.num, self.den)

    def __add__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.den + self.den * other.num
        self.den = self.den * other.den
        self.simplify()
        return self

    def __sub__(self, other):
        return self + other*(-1)

    def __eq__(self, other):
        if type(other) == Fraction:
            return self.num == other.num and self.den == other.den
        else:
            return self.num / self.den == other

    def to_real(self) -> float:
        return self.num / self.den

    def recip(self) -> Frac:
        self.num, self.den = self.den, self.num
        return self

    def simplify(self) -> None:
        if self.num == 0:
            # Fraction is zero so don't try and simplify
            return
        int_num = to_int(self.num)
        int_den = to_int(self.den)
        if type(int_num) == int and type(int_den) == int:
            num_f = factoriseNum(int_num)
            den_f = factoriseNum(int_den)
            # Simplify the fraction by removing factors of den from num
            # and factors of num from den
            new_num_f = list((Counter(num_f)-Counter(den_f)).elements()) + [1]
            new_den_f = list((Counter(den_f) - Counter(num_f)).elements()) + [1]

            self.num = product(new_num_f)
            self.den = product(new_den_f)
        else:
            return

    def __mul__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.num
        self.den = self.den * other.den
        self.simplify()
        return self

    def __pow__(self, power, modulo=None):
        self.num = self.num ** power
        self.den = self.den ** power
        return self

    def __lt__(self, other):
        if type(other) == Fraction:
            return self.to_real() < other.to_real()
        else:
            return self.to_real() < other
