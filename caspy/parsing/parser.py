import os
import inspect
import logging
from lark import Lark
import caspy.parsing.simplify_output

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, output="ASCII"):
        self.parser = Lark.open(os.path.join(os.path.dirname(inspect.stack()[0][1]), "grammar.lark"))
        self.simplifier_transformer = caspy.parsing.simplify_output.SimplifyOutput()

    def parse(self, line: str):
        tree = self.parser.parse(line)
        logger.debug("Tree = \n{}\n--".format(tree.pretty()))
        simped = self.simplifier_transformer.transform(tree)
        return simped
