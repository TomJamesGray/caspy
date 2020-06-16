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
            "level": logging.INFO}
    },
    "loggers": {
        "":{
            "handlers":["f_parsing"],
            "level":logging.INFO
        },
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

def main():
    parser_cls = parser.Parser()

    while True:
        line = input(">> ")
        print(parser_cls.parse(line))
