import copy
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from typing import TypeVar, Generic

Num = TypeVar("Num")


class Numeric(Generic[Num]):
    """Represents a linear combination of numbers and symbols"""

    def __init__(self, val: str, typ: str):
        """Initialises a numeric class with a single value"""
        self.val = []
        if typ == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val.append(Symbol(val, Fraction(1, 1)))
        elif typ == "number":
            # in this case the 1 represents that this value is just a number
            self.val.append(Symbol(1, Fraction(float(val), 1)))

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

    def pow(self,x: Num) -> Num:
        """
        Raises this number to the power x
        :param x: Numeric object
        :return: self
        """
        # Make a copy of this object for later use
        pre_exp = copy.copy(self)
        # Redefine this object as a list of length 1 with the previous
        # info stored as a symbol type and raise that to the power x
        self.val = [Symbol(pre_exp, Fraction(1, 1))]
        self.val[0].val[pre_exp] = x
        return self

    def mul(self,x: Num) -> Num:
        """
        Multiplies this number by x. If this number or x is made up
        of a linear combination of terms, eg (1+x) then we don't
        expand the product
        :param x: Numeric object
        :return: self
        """
        if len(self.val) > 1 or len(x.val) > 1:
            pre_self = copy.copy(self)
            pre_x = copy.copy(x)
            self.val = [Symbol(pre_self, Fraction(1, 1))]
            self.val[0].val[pre_x] = Numeric(1,"number")
        else:
            self.val[0].mul(x.val[0])
        return self
