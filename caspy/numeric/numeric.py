from caspy.numeric.symbol import Symbol

class Numeric:
    """Represents a linear combination of numbers and symobols"""
    def __init__(self,val: str,type: str):
        """Initialises a numeric class with a single value"""
        self.val = {}
        if type == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val[Symbol(val)] = 1
        elif type == "number":
            # in this case the 1 represents that this value is just a number
            self.val["1"] = float(val)

    def __repr__(self):
        return "<Numeric class {}>".format(self.val)

    def add(self,y):
        """
        Adds y to this number
        :param y: Another numeric class
        :return: self
        """
        for key in y.val:
            if key in self.val:
                self.val[key] += y.val[key]
            else:
                self.val[key] = y.val[key]

        return self

    def neg(self):
        """
        Negates this number
        :return: self
        """
        for key in self.val:
            self.val[key] *= -1

        return self

    def mul(self,y):
        """
        Multiplies this  number by y
        :param y: Numeric object
        :return: self
        """
        for key_y in y.val:
            if key_y == "1":
                for key_s in self.val:
                    self.val[key_s] *= y.val[key_y]

        return self

    # def pow(self,y):
    #     """
    #     Raises this number to the power y
    #     :param y: Numeric object
    #     :return: self
    #     """
    #     for key_y
