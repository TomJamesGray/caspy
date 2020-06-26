from caspy.functions.function import Function1Arg


class TrigFunc(Function1Arg):
    pass


class Sin(TrigFunc):
    fname = "sin"
    latex_fname = "\\sin"
    set_points = [
        ["pi/2","1"],
        ["pi/4","2^(-1/2)"]
    ]

    def __init__(self,x):
        self.arg = x
        super().__init__()
