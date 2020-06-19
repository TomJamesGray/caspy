import logging
from lark import v_args
from lark import Transformer
from caspy.numeric.numeric import Numeric

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
@v_args(inline=True)
class SimplifyOutput(Transformer):
    """
    Transformer that applies some basic simplification to lark AST to be used
    before outputting
    """

    def number(self, x: str) -> Numeric:
        return Numeric(x, "number")

    def sym(self, x) -> Numeric:
        return Numeric(str(x), "sym")

    def add(self, x: Numeric, y: Numeric) -> Numeric:
        return x.add(y)

    def neg(self, x: Numeric) -> Numeric:
        return x.neg()

    def sub(self, x: Numeric, y: Numeric) -> Numeric:
        return x.add(y.neg())

    def mul(self, x: Numeric, y: Numeric) -> Numeric:
        return x.mul(y)
