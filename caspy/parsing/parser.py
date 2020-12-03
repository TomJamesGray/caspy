import os
import inspect
import logging
from lark import Lark
import caspy.parsing.simplify_output

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, output="ASCII"):
        self.parser = Lark(r"""
        ?start:expr
        | NAME ":=" expr -> def_expr

        ?expr: sum
            | expr "=" sum -> equality
        
        ?sum: product
            | sum "+" product -> add
            | sum "-" product -> sub
        
        ?product:negation
            | product "*" negation -> mul
            | product "/" negation -> div
        
        ?negation:power
            | "-" power -> neg
        
        ?power:atom
            | power "^" atom -> pow
        
        ?atom: NAME "(" paramaters? ")" -> func_call
            | "[" paramaters? "]" -> gen_arr
            | NUMBER -> number
            | "(" sum ")"
            | /("([^"]|"")*")+/ -> string
            | NAME -> sym
        
        
        
        paramaters: (paramvalue ("," paramvalue)* ("," kwargs)* | kwargs ("," kwargs)* )
        
        kwargs: NAME "=" (atom | sum)
        
        paramvalue:atom | sum
        
        %import common.NUMBER
        %import common.WS_INLINE
        %import common.CNAME -> NAME
        
        %ignore WS_INLINE
        """)
        self.simplifier_transformer = caspy.parsing.simplify_output.SimplifyOutput()
        self.simplifier_transformer.parser_cls = self

    def parse(self, line: str):
        tree = self.parser.parse(line)
        logger.debug("Tree = \n{}\n--".format(tree.pretty()))
        simped = self.simplifier_transformer.transform(tree)
        return simped
