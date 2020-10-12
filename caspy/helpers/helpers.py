import itertools
from math import gcd
from functools import reduce


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


def get_divisors(num):
