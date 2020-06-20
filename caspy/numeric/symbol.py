class Symbol:
    """Represents a product of symbols and their powers"""
    def __init__(self, val: str):
        self.val = {val: 1}

    def mul(self, y):
        for key in y.val:
            if key in self.val:
                self.val[key] += y.val[key]
            else:
                self.val[key] = y.val[key]

        return self

    def __eq__(self, other):
        return self.val == other.val

    def __hash__(self):
        return hash(str(self.val))

    def __repr__(self):
        return str(self.val)
