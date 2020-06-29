from caspy.functions.function import Function1Arg
from caspy.pattern_match import pmatch


class TrigFunc(Function1Arg):
    pass


class Sin(TrigFunc):
    fname = "sin"
    latex_fname = "\\sin"
    set_points = [
        ["pi/2","1"],
        ["pi/3", "3^(1/2)/2"],
        ["pi/4","2^(-1/2)"],
        ["pi/6","1/2"],
        ["pi","0"],
        ["0","0"]
    ]

    def __init__(self,x):
        self.arg = x
        super().__init__()

    def eval(self):
        print("PAT MATCH: {}".format(pmatch("a*pi",self.arg,{"a":"const"})))
        return super().eval()
