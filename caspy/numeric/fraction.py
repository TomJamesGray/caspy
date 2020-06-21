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
        if self.den == 1:
            return str(self.num)
        else:
            return "{}/{}".format(self.num, self.den)

    def __add__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.den + self.den * other.num
        self.den = self.den * other.den

        return self

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

    def __mul__(self, other) -> Frac:
        if type(other) != Fraction:
            other = Fraction(float(other), 1)

        self.num = self.num * other.num
        self.den = self.den * other.den

        return self

