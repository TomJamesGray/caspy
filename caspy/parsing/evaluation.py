import logging
from lark import v_args
from lark import Transformer

logger = logging.getLogger(__name__)


@v_args(inline=True)
class EvalLine(Transformer):
    number = float

    def __init__(self, *args, **kwargs):
        super(EvalLine, self).__init__(*args, **kwargs)

    def add(self, x, y):
        logger.info("x = {}, y = {}".format(x, y))
        return 1

    def unpack_args(self, x):
        """
        Unpacks *args sent by lark
        :param x: The args paramater
        :return:
        """
        for val in x[0].children:
            if len(val.children) > 1:
                yield tuple([x for x in val.children])
            else:
                yield val.children[0]

    def func_call(self, name, *args):
        logger.info("name = {}, args = {}".format(name, args))
        unpacked = []
        for val in self.unpack_args(args):
            unpacked.append(val)

        logger.info("Unpacked args = {}".format(unpacked))
        return 0
