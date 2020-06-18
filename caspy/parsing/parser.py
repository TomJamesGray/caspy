import os
import inspect
import logging
from lark import Lark
from caspy.parsing import evaluation
from caspy.printing.ascii_print import ASCIIPrint
from caspy.parsing.simplify_output import SimplifyOutput

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, output="ASCII"):
        self.parser = Lark.open(os.path.join(os.path.dirname(inspect.stack()[0][1]), "grammar.lark"))
        self.eval = evaluation.EvalLine()
        self.simplifier_transformer = SimplifyOutput()
        if output == "ASCII":
            self.outputTrans = ASCIIPrint()


    def parse(self, line: str):
        tree = self.parser.parse(line)
        logger.debug("Tree = \n{}\n--".format(tree.pretty()))
        simped = self.simplifier_transformer.transform(tree)
        return simped
        return self.outputTrans.transform(simped)
