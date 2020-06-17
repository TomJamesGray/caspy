import logging
from lark import v_args
from lark import Transformer

logger = logging.getLogger(__name__)

@v_args(inline=True)
class SimplifyOutput(Transformer):
    """
    Transformer that applies some basic simplification to lark AST to be used
    before outputting
    """
    number = float

    # def __init__(self, *args, **kwargs):
    #     super(SimplifyOutput, self).__init__(*args, **kwargs)

    # def number(self,tree):
    #     logger.info("Number tree = {}".format(tree))
    #     return 23.4

    def div(self,x,y):
        logger.info("Simplifier: x = {} y = {}".format(x,y))
        # return None