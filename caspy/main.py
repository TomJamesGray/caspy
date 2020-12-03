import logging
import logging.config
from lark.exceptions import VisitError
from timeit import default_timer as timer
from caspy.parsing import parser
from caspy.printing.ascii_numeric import ascii_numeric_str
from caspy.printing.latex_numeric import latex_numeric_str

from logging.handlers import SocketHandler

logging_config = {
    "version":1,
    "disable_existing_loggers":False,
    "formatters": {
        "main": {"format": "%(levelname)s-%(name)s-%(lineno)d: %(message)s"}
    },
    "handlers": {
        "numeric": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": logging.DEBUG},
        "functions": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": logging.DEBUG},
        "cutelog": {
            "class": "logging.handlers.SocketHandler",
            "host": "127.0.0.1",
            "port": "19996"
        }
    },
    "loggers": {
        "":{
            "handlers":["numeric","cutelog"],
            "level":logging.WARNING
        },
        "caspy.numeric":{
            "handlers":["numeric","cutelog"],
            "level":logging.WARNING
        },
        "caspy.pattern_match":{
            "handlers":["functions","cutelog"],
            "level":logging.WARNING
        },
        "caspy.functions":{
            "handlers":["functions","cutelog"],
            "level":logging.DEBUG
        }
    }
}


logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

defined_vars = {}


def profile_me():
    parser_cls = parser.Parser(output="ASCII")
    parser_cls.parse("integrate(x*cos(ln(x)))")
    return True


def main():
    parser_cls = parser.Parser(output="ASCII")

    while True:
        line = input(">> ")
        try:
            start = timer()
            out = parser_cls.parse(line)
            end = timer()
            print("Time elapsed: {}s".format(end-start))
        except ZeroDivisionError:
            print("Math Error: Division by zero")
            continue
        print("Parser output = {}".format(out))
        print("ASCII:")
        print(ascii_numeric_str(out))
        print("\nLaTeX:")
        tex = latex_numeric_str(out)
        print(tex)
