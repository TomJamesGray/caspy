from caspy.numeric.fraction import Frac


class Symbol:
    """Represents a product of symbols and their powers"""
    def __init__(self, val: str, coeff: Frac):
        self.val = {val: 1}
        self.coeff = coeff

    def mul(self, y):
        for key in y.val:
            if key in self.val:
                self.val[key] += y.val[key]
            else:
                self.val[key] = y.val[key]

        return self

    def add_coeff(self, x: Frac) -> None:
        self.coeff = self.coeff + x

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

