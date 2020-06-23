import copy
import logging
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction
from typing import TypeVar, Generic

Num = TypeVar("Num")
logger = logging.getLogger(__name__)


class Numeric(Generic[Num]):
    """Represents a linear combination of numbers and symbols"""

    def __init__(self, val, typ: str):
        """Initialises a numeric class with a single value"""
        self.val = []
        if typ == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val.append(Symbol(val, Fraction(1, 1)))
        elif typ == "number":
            # in this case the 1 represents that this value is just a number
            self.val.append(Symbol(1, Fraction(float(val), 1)))
        elif typ == "sym_obj":
            self.val.append(val)

    def __repr__(self):
        return "<Numeric class {}>".format(self.val)

    def __add__(self, other):
        if type(other) == Numeric:
            return self.add(other)
        elif type(other) in (int,float):
            return self.add(Numeric(other, "number"))

    def __mul__(self, other):
        if type(other) == Numeric:
            return self.mul(other)

    def __sub__(self, other):
        if type(other) == Numeric:
            return self.add(other.neg())

    def __truediv__(self, other):
        if type(other) == Numeric:
            return self.mul(other.recip())

    def sym_in(self,key):
        """
        Checks if a symbol such as 'x' already exists in this. Used
        for multiplication of terms like x and x^2
        :param key: symbol such as x
        :return: False if not found, otherwise returns coresponding
        key for this object
        """
        for key_x in self.val:
            if key_x == key:
                return key_x
        return False

    def sym_and_pow_match(self,sym):
        """
        Checks if a s
        :param key: symbol object
        :return:
        """
        for sym_self in self.val:
            if sym_self == sym:
                return sym_self

        return False
    def add(self, y: Num) -> Num:
        """
        Adds y to this number
        :param y: Another numeric class
        :return: self
        """
        for sym_y in y.val:
            lookup = self.sym_and_pow_match(sym_y)
            if lookup:
                # A term with the same symbols already exists in this numeric expression
                # so just add coeffs
                print(self.sym_and_pow_match(sym_y))
                lookup.add_coeff(sym_y.coeff)
            else:
                self.val.append(sym_y)

        return self

    def neg(self) -> Num:
        """
        Negates this number
        :return: self
        """
        for sym in self.val:
            sym.neg()

        return self

    def recip(self) -> Num:
        if len(self.val) == 1:
            self.val[0] = self.val[0].recip()
            return self
        else:
            return self.pow(Numeric(-1,"number"))


    def pow(self,x: Num) -> Num:
        """
        Raises this number to the power x
        :param x: Numeric object
        :return: self
        """
        if len(self.val) == 1:
            self.val[0] = self.val[0].pow(x)
            return self
        else:
            # Make a copy of this object for later use
            pre_exp = copy.copy(self)
            # Redefine this object as a list of length 1 with the previous
            # info stored as a symbol type and raise that to the power x
            self.val = [Symbol(pre_exp, Fraction(1, 1))]
            self.val[0].val[0][1] = x
            return self

    def mul(self, x: Num) -> Num:
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

    def div(self,x: Num) -> Num:
        """
        Divides this number by x
        :param x: Numeric object
        :return: self
        """
        return self.mul(x.recip())

    def __hash__(self):
        return hash(str(self.val))

    def __eq__(self, other):
        if type(other) == Numeric:
            # for sym in self.val:
            #     if sym.val != self
            for sym in self.val:
                fnd = False
                for sym_o in other.val:
                    if sym_o.val == sym.val and sym_o.coeff == sym.coeff:
                        fnd = True
                if not fnd:
                    return False
            return True
