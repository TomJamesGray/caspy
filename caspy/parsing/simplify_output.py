import logging
from lark import v_args
from lark import Transformer
from caspy.numeric.numeric import Numeric

logger = logging.getLogger(__name__)

@v_args(inline=True)
class SimplifyOutput(Transformer):
    """
    Transformer that applies some basic simplification to lark AST to be used
    before outputting
    """
    def number(self,x: str) -> Numeric:
        return Numeric(x,"number")

    def sym(self,x: str) -> Numeric:
        return Numeric(x,"sym")

    def add(self,x: Numeric,y: Numeric) -> Numeric:
        logger.info("adding x = {}, y = {}".format(x,y))
        return x.add(y)
