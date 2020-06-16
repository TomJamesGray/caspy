import logging
import logging.config
from caspy.parsing import parser

logging_config = {
    "version":1,
    "disable_existing_loggers":False,
    "formatters": {
        "main": {"format": "%(levelname)s-%(name)s-%(lineno)d: %(message)s"}
    },
    "handlers": {
        "f_parsing": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": logging.DEBUG}
    },
    "loggers": {
        "":{
            "handlers":["f_parsing"],
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
        print(parser_cls.parse(line))
