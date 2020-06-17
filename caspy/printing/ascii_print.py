import logging
from lark import Transformer,v_args,Tree

logger = logging.getLogger(__name__)


@v_args(inline=True)
class ASCIIPrint(Transformer):
    """
    Lark tree transformer that turns a lark AST to an ASCII string
    """
    number = str
    sym = str

    def __init__(self,*args,**kwargs):
        super(ASCIIPrint, self).__init__(*args, **kwargs)

    def add(self,x,y):
        return "{} + {}".format(x,y)

    def div(self,x,y):
        # logger.info("x = {},y = {}".format(x,y))
        return "({})/({})".format(x,y)

    def sub(self,x,y):
        return "{}-{}".format(x,y)

    def pow(self,x,y):
        return "{}^{}".format(x,y)

    def mul(self,x,y):
        return "{}*{}".format(x,y)
