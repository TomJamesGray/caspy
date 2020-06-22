class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg

    def __hash__(self):
        return hash("{}({})".format(self.fname,self.arg))

class Function1Arg:
    pass