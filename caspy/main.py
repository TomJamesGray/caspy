import logging
import argparse
import logging.config
from argparse import RawTextHelpFormatter
from lark.exceptions import VisitError
from timeit import default_timer as timer
from caspy.parsing import parser
from caspy.printing.ascii_numeric import ascii_numeric_str
from caspy.printing.latex_numeric import latex_numeric_str


def main(args):

    a_parser = argparse.ArgumentParser(description="""
Caspy - A CAS built in Python

Available functions in the system:
- integrate(f(x),x) : Integrate a function with respect to a variable x
- diff(f(x),x) : Differentiates a function with respect to a variable x
- factor(f(x)) : Factorises a polynomial g(x) using Kronecker's algorithm
- expand_trig(...) : Expands a trigonometric expression, for instance
                      sin(2x) is expanded as 2sin(x)cos(x)
- expand(...) : Expands brackets in an expression 
- re(...) : Returns floating point answer where possible, for instance
            re(sqrt(2)) gives 1.4142...
    """,formatter_class=RawTextHelpFormatter)
    a_parser.add_argument("--timer",action="store_true",default=False,
                        help="Time execution of statements")
    a_parser.add_argument("--verbose",action="store_true",default=False,
                        help="Enable verbose logging")
    a_parser.add_argument("--debug",action="store_true",default=False,
                        help="Enable more verbose logging for debugging purposes")
    a_parser.add_argument("--ascii",action="store_true",default=False,
                          help="Output string using ASCII characters")
    a_parser.add_argument("--latex",action="store_true",default=False,
                          help="Output representation of string in LaTeX form")
    a_parser.add_argument("--unicode", action="store_true", default=False,
                          help="Output string using Unicode characters")

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
    # parser_cls.parse("factor(3x^9+x^3+10x^2)")
    # return None
    if not args_results.ascii:
        args_results.ascii = not (args_results.latex or args_results.unicode)
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
        if args_results.verbose or args_results.debug:
            print("Parser output = {}".format(out))
        if args_results.ascii:
            print(latex_numeric_str(out,"ascii"))
        if args_results.latex:
            print(latex_numeric_str(out,"latex"))
        if args_results.unicode:
            print(latex_numeric_str(out, "unicode"))
