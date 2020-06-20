from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from typing import TypeVar, Generic

Num = TypeVar("Num")


class Numeric(Generic[Num]):
    """Represents a linear combination of numbers and symobols"""

    def __init__(self, val: str, typ: str):
        """Initialises a numeric class with a single value"""
        self.val = []
        if typ == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val.append(Symbol(val, Fraction(1, 1)))
        elif typ == "number":
            # in this case the 1 represents that this value is just a number
            self.val.append(Symbol("1", Fraction(float(val), 1)))

    def __repr__(self):
        return "<Numeric class {}>".format(self.val)

    def sym_in(self,key):
        for key_x in self.val:
            if key_x == key:
                return key_x
        return False

    def add(self, y: Num) -> Num:
        """
        Adds y to this number
        :param y: Another numeric class
        :return: self
        """
        for sym_y in y.val:
            lookup = self.sym_in(sym_y)
            if lookup:
                # A term with the same symbols already exists in this numeric expression
                # so just add coeffs
                lookup.add_coeff(sym_y.coeff)
            else:
                self.val.append(sym_y)


        return self

    def neg(self) -> Num:
        """
        Negates this number
        :return: self
        """
        for key in self.val:
            self.val[key] *= -1

        return self
