# Copyright (c) 2021, COMU Team, Osman Ceylan and etc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the COMU Team organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ctypes
import base64
import random
import string
import threading
import numpy as np

# Dev mode.
# Opens backends log.
dev_mode = False

digs = string.digits + string.ascii_letters


def string_encode(key, clear):
    key = np.array(key, dtype=int)
    key = np.array_str(key)
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def string_decode(key, enc):
    key = np.array(key, dtype=int)
    key = np.array_str(key)
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    """ Generates sized random chars. """

    return ''.join(random.choice(chars) for _ in range(size))


def flush_queue(a_queue):
    """ Flushes queues. """

    while not a_queue.empty():
        a_queue.get()


def int2base(x, count, base):
    """ Base changer. """

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
def fiber_formula(length, loss_rate=11.447):
    total = 1 - np.power(10, ((-1 * length * loss_rate / 100) / 10))

    # Add slight randomness.
    total = np.random.uniform(total * 91 / 100, total)

    # Probability limits.
    if total > 1:
        total = 0.99

    return total


def tensordot(state_first, state_second):
    """
    Vectorel circuit state specialized tensordot product.
    Return new merged state.
    """

    source_row = state_first.shape[0]
    target_row = state_second.shape[0]

    try:
        source_column = state_first.shape[1]
    except IndexError:
        source_column = 1
    try:
        target_column = state_second.shape[1]
    except IndexError:
        target_column = 1

    new_shape = (source_row * target_row, source_column * target_column)
    new_state = np.zeros(shape=new_shape, dtype=complex)
    state_first = np.array(state_first).reshape((source_row, source_column))
    state_second = np.array(state_second).reshape((target_row, target_column))

    a, b = 0, 0
    c, d = 0, 0
    for i in range(new_shape[0]):
        for j in range(new_shape[1]):
            new_state[i][j] = state_first[a][b] * state_second[c][d]
            d += 1

            if d >= target_column:
                d = 0
                b += 1
        b = 0
        c += 1

        if c >= target_row:
            c = 0
            a += 1

    return new_state.transpose()[0]


def terminate_thread(thread):
    """
    Terminates the thread but not consistent solution,
    this because not always main thread calls this method.
    Child threads mostly call this for another child for most of time.
    Make sure call this function in try, except block.
    """

    if not thread.is_alive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("Nonexistent thread id")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class TerminatableThread(threading.Thread):
    def __init__(self, target_method, *data, daemon=False, args=None):
        """
        Thread with terminate call.

        Args:
            target_method: Method for threading.
            data: Any data to hold.
            daemon: Daemonize.
            args: Parameters.
        """

        if args is None:
            args = tuple()

        super().__init__(target=target_method, args=(*args,), daemon=daemon)
        self._data = data

    def terminate(self):
        """ Terminate thread. """

        terminate_thread(self)

    def data_(self, index):
        """ Gets the index of data. """

        try:
            return self._data[index]
        except (KeyError, IndexError):
            return None

    @property
    def data(self):
        return self._data
