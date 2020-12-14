import logging
import argparse
import logging.config
from lark.exceptions import VisitError
from timeit import default_timer as timer
from caspy.parsing import parser
from caspy.printing.ascii_numeric import ascii_numeric_str
from caspy.printing.latex_numeric import latex_numeric_str


def main(args):
    a_parser = argparse.ArgumentParser(description="Caspy - A CAS developed in Python")
    a_parser.add_argument("--timer",action="store_true",default=False,
                        help="Time execution of Caspy")
    a_parser.add_argument("--verbose",action="store_true",default=False,
                        help="Enable verbose logging")
    a_parser.add_argument("--debug",action="store_true",default=False,
                        help="Enable more verbose logging for debugging purposes")

    args_results = a_parser.parse_args(args)
    log_level = logging.ERROR
    if args_results.debug:
        log_level = logging.DEBUG
    elif args_results.verbose:
        log_level = logging.WARNING


    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "main": {"format": "%(levelname)s-%(name)s-%(lineno)d: %(message)s"}
        },
        "handlers": {
            "numeric": {
                "class": "logging.StreamHandler",
                "formatter": "main",
                "level": log_level},
            "functions": {
                "class": "logging.StreamHandler",
                "formatter": "main",
                "level": log_level},
            "cutelog": {
                "class": "logging.handlers.SocketHandler",
                "host": "127.0.0.1",
                "port": "19996"
            }
        },
        "loggers": {
            "": {
                "handlers": ["numeric", "cutelog"],
                "level": log_level
            },
            "caspy.numeric": {
                "handlers": ["numeric", "cutelog"],
                "level": log_level
            },
            "caspy.pattern_match": {
                "handlers": ["functions", "cutelog"],
                "level": log_level
            },
            "caspy.functions": {
                "handlers": ["functions", "cutelog"],
                "level": log_level
            }
        }
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)

    parser_cls = parser.Parser(output="ASCII")

    while True:
        line = input(">> ")
        try:
            start = timer()
            out = parser_cls.parse(line)
            end = timer()
            if args_results.timer:
                print("Time elapsed: {}s".format(end-start))
        except ZeroDivisionError:
            print("Math Error: Division by zero")
            continue
        # print("Parser output = {}".format(out))
        # print("ASCII:")
        # print(ascii_numeric_str(out))
        # print("\nLaTeX:")
        tex = latex_numeric_str(out)
        print(tex)
