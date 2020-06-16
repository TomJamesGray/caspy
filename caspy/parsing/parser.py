from lark import Lark
import os
import inspect

class Parser:
    def __init__(self):
        self.parser = Lark.open(os.path.join(os.path.dirname(inspect.stack()[0][1]), "grammar.lark"))

    def parse(self,line:str):
        tree = self.parser.parse(line)
        return tree