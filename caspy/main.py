import logging
import logging.config
from caspy.parsing import parser
from caspy.printing.ascii_numeric import ascii_numeric_str
from caspy.printing.latex_numeric import latex_numeric_str

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
            "level": logging.WARNING},
        "functions": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": logging.DEBUG}
    },
    "loggers": {
        "":{
            "handlers":["numeric"],
            "level":logging.WARNING
        },
        "caspy.numeric":{
            "handlers":["numeric"],
            "level":logging.WARNING
        },
        "caspy.functions":{
            "handlers":["functions"],
            "level":logging.DEBUG
        },
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

defined_vars = {}


def main():
    parser_cls = parser.Parser(output="ASCII")

    while True:
        line = input(">> ")
        out = parser_cls.parse(line)
        print("Parser output = {}".format(out))
        print("ASCII:")
        print(ascii_numeric_str(out))
        print("\nLaTeX:")
        tex = latex_numeric_str(out)
        print(tex)