import logging
from lark import v_args
from lark import Transformer
from caspy.numeric.numeric import Numeric
from caspy.helpers import lark_transformer
from caspy.functions import exponentials,trigonometric,other
from caspy.functions.cas import expand,integrate,differentiate

logger = logging.getLogger(__name__)

fns = {
    "ln": lambda x: exponentials.Ln(x),
    "sin": lambda x: trigonometric.Sin(x),
    "cos": lambda x: trigonometric.Cos(x),
    "tan": lambda x: trigonometric.Tan(x),
    "sqrt": lambda x: other.Sqrt(x),
    "expand": lambda x: expand.Expand(x),
    "integrate": lambda *args: integrate.Integrate(*args),
    "diff": lambda *args: differentiate.Differentiate(*args)
}

# noinspection PyMethodMayBeStatic
@v_args(inline=True)
class SimplifyOutput(Transformer,lark_transformer.LarkTransformerHelper):
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

    def div(self, x: Numeric, y: Numeric) -> Numeric:
        return x.div(y)

    def pow(self, x: Numeric, y: Numeric) -> Numeric:
        return x.pow(y)

    def func_call(self, fname, *args):
        # Unpack arguments into a list
        unpacked = []
        for val in self.unpack_args(args):
            unpacked.append(val)

        if fname in fns:
            func = fns[fname](*unpacked)
            return func.eval()
