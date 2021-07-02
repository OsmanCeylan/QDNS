"""
##======================================================================##
##  Header of QDNS/tools/various_tools.py                              ##
##======================================================================##

##======================================================================##
## Brief                                                                ##
## Contains various python tools.                                       ##
##======================================================================##
"""

import random
import string
import numpy as np

digs = string.digits + string.ascii_letters


def string_encode(key, string_: str):
    """
    Simple string encode.

    Args:
        key: List of int.
        string_: message.

    Returns:
        string
    """

    encoded_chars = []
    for i in range(len(string_)):
        key_c = str(key[i % len(key)])
        encoded_c = chr(ord(string_[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string


def string_decode(key, string_: str):
    """
    Simple string decode.

    Args:
        key: List of int.
        string_: message.

    Returns:
        string
    """

    encoded_chars = []
    for i in range(len(string_)):
        key_c = str(key[i % len(key)])
        encoded_c = chr((ord(string_[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string


def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def flush_queue(a_queue):
    while not a_queue.empty():
        a_queue.get()


def int2base(x, count, base):
    digits = []
    if x < 0:
        sign = -1
    elif x == 0:
        for i in range(count):
            digits.append('0')
        return ''.join(digits)
    else:
        sign = 1

    x *= sign

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    if count > digits.__len__():
        for i in range(count - digits.__len__()):
            digits.append('0')
    digits.reverse()

    return ''.join(digits)


# 1680 nanometer Rayleigh scattering on Fibre cable.
def fiber_formula(length, loss_rate=11.3334):
    total = 1 - np.power(10, ((-1 * length * loss_rate / 100) / 10))

    # Add slight randomness.
    total = np.random.uniform(total * 91 / 100, total)

    # Probability limits.
    if total > 1:
        total = 0.99

    return total
