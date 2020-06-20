import logging
import caspy.numeric.numeric as num
from caspy.numeric.fraction import Frac

logger = logging.getLogger(__name__)

class Symbol:
    """Represents a product of symbols and their powers"""
    def __init__(self, val, coeff: Frac):
        if val == 1:
            self.val = {val: 1}
            self.coeff = coeff
        else:
            self.val = {val: num.Numeric(1,"number")}
            self.coeff = coeff

    def mul(self, y):
        for key in y.val:
            if key in self.val:
                self.val[key] += y.val[key]
            else:
                self.val[key] = y.val[key]
        self.coeff *= y.coeff
        return self

    def add_coeff(self, x: Frac) -> None:
        self.coeff = self.coeff + x

    def neg(self):
        """Negates this symbol"""
        self.coeff *= -1

    def pow(self,x):
        """Raises this symbol to the power x"""
        logger.info("{} to the power {}".format(self,x))
        for key in self.val:
            if type(self.val[key]) == num.Numeric:
                self.val[key] = self.val[key].mul(x)
            else:
                self.val[key] = x.mul(num.Numeric(self.val[key],"number"))

        self.coeff = self.coeff.recip()

        return self

    def recip(self):
        """Makes this symbol the reciprocal of itself"""
        for key in self.val:
            if type(self.val[key]) == num.Numeric:
                self.val[key] = self.val[key].neg()
            else:
                self.val[key] = - self.val.key()

        self.coeff = self.coeff.recip()

        return self

    def __repr__(self):
        return "<Symbol {},{}>".format(self.coeff,self.val)

    def __eq__(self, other):
        """
        Defines 2 symbols as being equal if they have the same keys
        in the value dictionary
        :param other: Thing being compared
        :return: Boolean
        """
        if type(other) == Symbol:
            return self.val.keys() == other.val.keys()
        else:
            return False

    # def __mul__(self, x):

