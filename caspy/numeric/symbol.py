import logging
import caspy.numeric.numeric as num
from caspy.numeric.fraction import Frac

logger = logging.getLogger(__name__)


class Symbol:
    """Represents a product of symbols and their powers"""
    def __init__(self, val, coeff: Frac):
        if val == 1:
            # Store value as a list of pair lists, ie
            # [[value1,power1],[value2,power2]] so x^2*y would be
            # [['x',Numeric(2)],['y',Numeric(1)]]
            # The value part can be a string like 'x' or a Numeric object
            # like (1+x)
            self.val = [[val, 1]]
            self.coeff = coeff
        else:
            self.val = [[val, num.Numeric(1,"number")]]
            self.coeff = coeff

    def __mul__(self, other):
        if type(other) == Symbol:
            for j in range(0,len(other.val)):
                sym_added = False
                for i in range(0, len(self.val)):
                    if self.val[i][0] == other.val[j][0] and self.val[i][0] != 1:
                        # Symbols match so increment the powers
                        self.val[i][1] += other.val[j][1]
                        sym_added = True
                        # Leave this loop
                        break
                if not sym_added:
                    self.val.append(other.val[j])

            self.coeff *= other.coeff
            return self

    def __pow__(self, power):
        """
        Raises this symbol to the power x
        :param power: Numeric object
        :return: self
        """
        if type(power) == num.Numeric:
            for i in range(0,len(self.val)):
                if type(self.val[i][1]) == num.Numeric:
                    self.val[i][1] = self.val[i][1].mul(power)
                else:
                    self.val[i][1] = power.mul(num.Numeric(self.val[i][1],"number"))
            return self

    def mul(self, y):
        return self * y

    def pow(self,x):
        """
        Raises this symbol to the power x
        :param x: Numeric object
        :return: self
        """
        return self ** x

    def add_coeff(self, x: Frac) -> None:
        self.coeff = self.coeff + x

    def neg(self):
        """Negates this symbol"""
        self.coeff *= -1

    def recip(self):
        """Makes this symbol the reciprocal of itself"""
        for i in range(0,len(self.val)):
            if type(self.val[i][1]) == num.Numeric:
                self.val[i][1] = self.val[i][1].neg()
            else:
                self.val[i][1] = - self.val[i][1]
        self.coeff = self.coeff.recip()
        return self

    def __repr__(self):
        return "<Symbol {},{}>".format(self.coeff,self.val)

    def __eq__(self, other):
        """
        Defines equality for the symbol class. The order of the terms
        in the value property doesn't matter. Ignores the coefficient
        property
        """
        if type(other) == Symbol:
            for (sym_name,pow) in self.val:
                eq = False
                for (sym_name_o,pow_o) in other.val:
                    if sym_name == sym_name_o and pow == pow_o:
                        eq = True
                        break

                if not eq:
                    return False

            return True
        else:
            return False
