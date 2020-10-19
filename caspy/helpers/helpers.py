import itertools
import collections
from math import gcd
from functools import reduce
from caspy.factorise import factoriseNum


def group_list_into_all_poss_pairs(lst):
    """
    Splits list into all possible groupings. So for example the list
    [1,2,3] could be split into
    [1],[2,3]
    [2],[1,3]
    [3],[1,2]
    Yields each pairing
    """
    length = len(lst)
    len_a = 1
    while len_a <= length / 2:
        for a in itertools.combinations(lst,len_a):
            a = list(a)
            b = []
            for val in lst:
                if val not in a:
                    b.append(val)

            yield a, b
        len_a += 1


def lcm(nums):
    """
    Returns the lowest common multiple of a list of ints
    """
    return reduce(lambda a, b: a * b // gcd(a, b), nums)


def gcd_l(nums):
    """
    Returns the greatest common divisor of a list of ints
    """
    return reduce(gcd, nums)

# Read from https://alexwlchan.net/2019/07/finding-divisors-with-python/


def prod(iterable):
    result = 1
    for i in iterable:
        result *= i
    return result


def get_divisors(num):
    factors = list(factoriseNum(num))[1:]
    pf_mults = collections.Counter(factors)

    powers = [
        [factor ** i for i in range(count+1)]
        for factor, count in pf_mults.items()
    ]

    for power_combo in itertools.product(*powers):
        yield prod(power_combo)


def leading_term(a):
    max_pow = deg(a)
    for power,coeff in a:
        if power == max_pow:
            return [power,coeff]


def term_div(x,y):
    """Divides polyn term x by term y"""
    return [x[0] - y[0], x[1] / y[1]]


def mul_polyn_by_term(x,y):
    """Multiplies polynomial x by term y"""
    return [
        [power + y[0], coeff * y[1]] for power,coeff in x
    ]


def deg(x):
    """Gets degree of polynomial x"""
    max_pow = 0
    for power,coeff in x:
        if power > max_pow and coeff != 0:
            max_pow = power
    return max_pow


def sub_polyns(x,y):
    """Subtracts polynomial y from x"""
    new_polyn = []
    for power in range(0,max([deg(x),deg(y)])):
        x_coeff = 0
        for x_pow,coeff in x:
            if x_pow == power:
                x_coeff = coeff
        y_coeff = 0
        for y_pow, coeff in y:
            if y_pow == power:
                y_coeff = coeff

        new_polyn.append([power,x_coeff - y_coeff])

    return new_polyn


def reformat_polyn(x):
    """
    Reformat polynomial from form used for polyn_div to the format it
    was given in the argument initially
    """
    n = deg(x)
    print("Reformat {}".format(x))
    new_polyn = [0 for _ in range(n+1)]
    for power,coeff in x:
        if power <= n:
            new_polyn[n-power] = coeff
    return new_polyn


def polyn_div(a,b):
    """
    Divides polynomial a by polynomial b, eg if a is x^2+2*x+3 it would be
    represented as [1,2,3]
    :param a: List representing polynomial
    :param b: List representing polynomial
    :return: List representing polynomial
    """
    a_polyn = [[i, x] for i, x in enumerate(a[::-1])]
    b_polyn = [[i, x] for i, x in enumerate(b[::-1])]
    quotient = []
    cur_polyn = a_polyn

    while deg(cur_polyn) >= deg(b_polyn):
        quotient_term = term_div(leading_term(cur_polyn), leading_term(b_polyn))
        to_subtract = mul_polyn_by_term(b_polyn, quotient_term)
        cur_polyn = sub_polyns(cur_polyn, to_subtract)
        quotient.append(quotient_term)
        if deg(cur_polyn) == 0:
            break
        # print("Cur polyn: {}\nto_sub:{}\nquotient:{}".format(cur_polyn,to_subtract,quotient))

    return reformat_polyn(quotient),reformat_polyn(cur_polyn)