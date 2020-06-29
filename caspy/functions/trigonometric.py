import logging
from caspy.functions.function import Function1Arg
from caspy.pattern_match import pmatch,pat_construct

logger = logging.getLogger(__name__)

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
        pat = pat_construct("a*pi",{"a":"const"})
        logger.debug("Constructed pattern {}".format(pat))
        pmatch(pat,self.arg)
        return super().eval()
