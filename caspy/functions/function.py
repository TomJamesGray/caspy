from caspy.parsing import parser as P

class Function:
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.fname == other.fname and self.arg == other.arg

    def __hash__(self):
        return hash("{}({})".format(self.fname,self.arg))


class Function1Arg(Function):
    def __init__(self):
        parser = P.Parser()
        self.evaled_set_points = []
        for (arg_val,f_val) in self.set_points:
            self.evaled_set_points.append([parser.parse(arg_val),parser.parse(f_val)])
