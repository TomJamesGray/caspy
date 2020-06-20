from typing import TypeVar,Generic

Frac = TypeVar("Frac")


class Fraction(Generic[Frac]):
    """
    Represents a fraction
    """
    def __init__(self,num: float, den: float):
        self.num = num
        self.den = den

    def __repr__(self):
        return "{}/{}".format(self.num, self.den)

    def __add__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.den + self.den * other.num
        self.den = self.den * other.den

        return self

    def __mul__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.num
        self.den = self.den * other.den

        return self

