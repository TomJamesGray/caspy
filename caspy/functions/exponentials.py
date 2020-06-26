from caspy.functions.function import Function1Arg


class Ln(Function1Arg):
    fname = "ln"
    latex_fname = "\\ln"
    set_points = [
        ["e","1"],
        ["e^2","2"]
    ]

    def __init__(self,x):
        self.arg = x
        super().__init__()
