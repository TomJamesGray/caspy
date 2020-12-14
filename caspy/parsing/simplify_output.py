import logging
from lark import v_args
from lark import Transformer
import caspy.numeric.numeric
# from caspy.numeric.numeric import Numeric
from caspy.helpers import lark_transformer
from caspy.functions import exponentials,trigonometric,other,to_real
from caspy.functions.cas import expand,integrate,differentiate,kronecker_factorise

logger = logging.getLogger(__name__)

fns = {
    "ln": lambda x: exponentials.Ln(x),
    "sin": lambda *x: trigonometric.Sin(*x),
    "cos": lambda *x: trigonometric.Cos(*x),
    "tan": lambda *x: trigonometric.Tan(*x),
    "sqrt": lambda x: other.Sqrt(x),
    "expand": lambda x: expand.Expand(x),
    "re": lambda x: to_real.ToReal(x),
    "integrate": lambda *args: integrate.Integrate(*args),
    "diff": lambda *args: differentiate.Differentiate(*args),
    "expand_trig": lambda x: expand.ExpandTrig(x),
    "factor": lambda x: kronecker_factorise.KroneckerFactor(x)
}

pass_parser_to = ["sin","cos","tan"]

# noinspection PyMethodMayBeStatic
@v_args(inline=True)
class SimplifyOutput(Transformer,lark_transformer.LarkTransformerHelper):
    """
    Transformer that applies some basic simplification to lark AST to be used
    before outputting
    """

    def number(self, x: str):
        return caspy.numeric.numeric.Numeric(x, "number")

    def sym(self, x):
        return caspy.numeric.numeric.Numeric(str(x), "sym")

    def add(self, x, y):
        return x.add(y)

    def neg(self, x):
        return x.neg()

    def sub(self, x, y):
        return x.add(y.neg())

    def mul(self, x, y):
        return x.mul(y)

    def div(self, x, y):
        return x.div(y)

    def pow(self, x, y):
        return x.pow(y)

    def sym_with_scalar(self,x,y):
        return y.mul(self.number(x))


    def func_call(self, fname, *args):
        # Unpack arguments into a list
        unpacked = []
        for val in self.unpack_args(args):
            unpacked.append(val)

        # if fname == "sin":
        #     return trigonometric.Sin(unpacked[0],self.parser_cls).eval()
        if fname in fns:
            if fname in pass_parser_to:
                unpacked.append(self.parser_cls)
                # func = fns[fname][0](*unpacked,self.parser_cls)
            func = fns[fname](*unpacked)
            return func.eval()
