class Numeric:
    def __init__(self,val: str,type: str):
        """Initialises a numeric class with a single value"""
        self.val = {}
        if type == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val[val] = 1
        elif type == "number":
            # in this case the 1 represents that this value is just a number
            self.val["1"] = float(val)

    def add(self,y):
        for key in y.val:
            if key in self.val:
                self.val[key] += y.val[key]
            else:
                self.val[key] = y.val[key]

        return self

    def __repr__(self):
        return "<Numeric class {}>".format(self.val)