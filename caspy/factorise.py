def factoriseNum(n: float) -> [int]:
    """
    Factorises a number n into it's prime factors (including -1 as a 'prime') if possible
    :param n: Float to factorise
    :return: list of prime factors
    """
    factors = []
    if int(n) == n and n != 0:
        n = int(n)
        if n < 0:
            factors.append(-1)
            n /= -1
        while n % 2 == 0:
            factors.append(2)
            n /= 2

        trial_f = 3
        while n > 1:
            if n % trial_f == 0:
                factors.append(trial_f)
                n /= trial_f
            else:
                trial_f += 2

    return factors
