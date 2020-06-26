import logging
import caspy.numeric.numeric as num
from caspy.numeric.fraction import Frac,Fraction

logger = logging.getLogger(__name__)


class Symbol:
    """Represents a product of symbols and their powers"""
    def __init__(self, val, coeff: Frac):
        # Store value as a list of pair lists, ie
        # [[value1,power1],[value2,power2]] so x^2*y would be
        # [['x',Numeric(2)],['y',Numeric(1)]]
        # The value part can be a string like 'x' or a Numeric object
        # like (1+x)
        if val == 1:
            self.val = [[coeff, 1]]
            # self.coeff = 1
        else:
            self.val = [[val, num.Numeric(1,"number")],[coeff, 1]]
            # self.coeff = 1

    def __mul__(self, other):
        if type(other) == Symbol:
            if self.val == [[1,1]]:
                logger.debug("current sym val is [[1,1]] so ignore it completely")
                self.val = other.val
            else:
                logger.debug("Multiply {} by {}".format(self,other))

                for j in range(0,len(other.val)):
                    sym_added = False
                    for i in range(0, len(self.val)):
                        if self.val[i][0] == other.val[j][0] and self.val[i][0] != 1:
                            # Symbols match so increment the powers
                            self.val[i][1] += other.val[j][1]
                            sym_added = True
                            # Leave this loop
                            break
                    if not sym_added and other.val[j] != [1, 1]:
                        self.val.append(other.val[j])

            # self.coeff *= other.coeff
            return self

    def __pow__(self, power):
        """
        Raises this symbol to the power x
        :param power: Numeric object
        :return: self
        """
        if type(power) == num.Numeric:
            logger.debug("{} to the power {}".format(self,power))
            for i in range(0,len(self.val)):
                if type(self.val[i][1]) == num.Numeric:
                    self.val[i][1] = self.val[i][1].mul(power)
                elif self.val[i][0] != 1:
                    # Check that the first term isn't one. If it is then it's pointless
                    # raising it's power and will only confusing the formatting
                    # of the output
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

    @property
    def coeff(self) -> Frac:
        index = self.get_coeff_index()
        if index != -1:
            return self.val[index][0]
        # This can occur in some cases like 2^2
        logger.info("No coefficient index found for object {} so treating coeff as 1".format(self))
        return Fraction(1, 1)

    def get_coeff_index(self) -> int:
        """
        Finds the index of the coefficient term for this symbol
        :return: -1 if no such term found, otherwise returns the index
        """
        for i in range(0,len(self.val)):
            if type(self.val[i][0]) == Fraction and self.val[i][1] == 1:
                # We have found the index of the coefficient term
                return i
        # Don't return False since 0 == False
        return -1

    def add_coeff(self, x: Frac) -> None:
        logger.debug("Adding coefficient {} to {}".format(x,self))
        coeff_index = self.get_coeff_index()
        if coeff_index != -1:
            # Increment the coefficient by x
            self.val[coeff_index][0] += x
        else:
            logger.info("No coefficient index found for object {}".format(self))

    def neg(self):
        """Negates this symbol"""
        coeff_index = self.get_coeff_index()
        if coeff_index != -1:
            # Multiply the coefficient index by 1
            self.val[coeff_index][0] *= -1
        else:
            logger.warning("No coefficient index found for object {} so adding one as -1".format(self))
            self.val.append([Fraction(-1,1),1])

    def recip(self):
        """Makes this symbol the reciprocal of itself"""
        for i in range(0,len(self.val)):
            if type(self.val[i][1]) == num.Numeric:
                self.val[i][1] = self.val[i][1].neg()
            else:
                self.val[i][1] = - self.val[i][1]
        # self.coeff = self.coeff.recip()
        return self

    def __repr__(self):
        return "<Symbol {}>".format(self.val)

    def __eq__(self, other):
        """
        Defines equality for the symbol class. The order of the terms
        in the value property doesn't matter. Ignores the coefficient
        property
        """
        if type(other) == Symbol:
            fnd_vals = []
            i = 0
            for (sym_name,pow) in self.val:
                eq = False
                # Ignoring the coefficient 'property'
                if type(sym_name) == Fraction and pow == 1:
                    fnd_vals.append(i)
                    i += 1
                    continue
                for (sym_name_o,pow_o) in other.val:
                    if sym_name == sym_name_o and pow == pow_o:
                        eq = True
                        fnd_vals.append(i)
                        i += 1
                        break

                if not eq:
                    return False
            # TODO possibly temporary way of ensuring equality is commutative
            # return True and other == self
            logger.debug("fnd_vals for {} are {}".format(self,fnd_vals))
            return True and fnd_vals == list(range(0,len(other.val)))
        else:
            return False
