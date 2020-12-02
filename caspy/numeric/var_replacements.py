import logging
import copy
import caspy.numeric.numeric
from caspy.printing.latex_numeric import latex_numeric_str as lns

logger = logging.getLogger(__name__)


def try_replace_numeric_with_var_divs(num_obj, x, y, MAX_DIVS=10):
    """
    Trys to replace some term (x) in this symbol with another variable. For
    instance we could try and replace the term x^2 in the symbol sin(x^2)
    with a variable u. So sin(x^2) would become sin(u). Trys doing this by
    repeated division
    :param num_obj: Numeric object containing terms to try and replace
    :param x: Numeric object
    :param y: Numeric object
    :param: MAX_DIVS: maxium amount of divisions to try
    :return: Another numeric object if it has been successful, otherwise None
    """
    vars_to_remove = x.get_variables_in()
    if num_obj.get_variables_in().intersection(vars_to_remove) == set():
        return num_obj
    logger.info("Starting divs val {}, x {}".format(lns(num_obj),lns(x)))

    for i in range(1, MAX_DIVS):
        num_obj = num_obj / copy.deepcopy(x)
        num_obj.simplify()
        logger.info("New sym num {} vars {} x {}".format(lns(num_obj), num_obj.get_variables_in(), x))
        if num_obj.get_variables_in().intersection(vars_to_remove) == set():
            power = caspy.numeric.numeric.Numeric(i, "number")
            num_obj * (copy.deepcopy(y) ** power)
            return num_obj
    return None


def try_replace_numeric_with_var_mults(num_obj, x, y, MAX_MULTS=10):
    """
    Trys to replace some term (x) in this symbol with another variable. For
    instance we could try and replace the term x^2 in the symbol sin(x^2)
    with a variable u. So sin(x^2) would become sin(u). Trys doing this by
    repeated division
    :param num_obj: Numeric object containing terms to try and replace
    :param x: Numeric object
    :param y: Numeric object
    :param: MAX_MULTS: maxium amount of multiplications to try
    :return: Another numeric object if it has been successful, otherwise None
    """
    vars_to_remove = x.get_variables_in()
    if num_obj.get_variables_in().intersection(vars_to_remove) == set():
        return num_obj
    for i in range(1, MAX_MULTS):
        num_obj = num_obj * copy.deepcopy(x)
        num_obj.simplify()
        logger.info("New sym num2 {} vars {} x {}".format(lns(num_obj), num_obj.get_variables_in(), x))
        if num_obj.get_variables_in().intersection(vars_to_remove) == set():
            power = caspy.numeric.numeric.Numeric(i, "number")
            num_obj / (copy.deepcopy(y) ** power)
            return num_obj
    return None
