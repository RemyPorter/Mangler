"""The objects in this module represent a series of operations
which can be performed against an array of samples. These
samples could theoretically be anything, but the core purpose
is audio data. All of these operations support multi-channel
audio as their core input, but may only operate on one channel, if
they desire."""

import random
from numpy.fft import fft, ifft, fft2, ifft2

class BaseOperation:
    """A base class which represents a chain of operations.
    This is essentially a singly-linked list, done this way
    to make it easy to chain operations together with a fluent
    syntax.

    >>> bop1 = BaseOperation()
    >>> bop1 &= BaseOperation()
    >>> bop1.next_op
    <BaseOperation>

    """
    def __init__(self, channel=None):
        self.next_op = None
        self.channel = channel

    def __and__(self, other):
        if self.next_op:
            self.next_op & other
        else:
            self.next_op = other
        return self

    def __call__(self, stream):
        if not self.channel is None:
            self.munge(stream[self.channel])
        else:
            self.munge(stream)
        if self.next_op:
            self.next_op(stream)

    def __repr__(self):
        return "<BaseOperation>"

    def munge(self, stream):
        pass

class MonoSwap(BaseOperation):
    """This swap operation grabs two segments on a single channel
    and swaps them.

    >>> s = MonoSwap(slice(0,4), slice(4,8))
    >>> data = [list(range(100)), list(range(100))]
    >>> s(data)
    >>> data[0][0:9]
    [4, 5, 6, 7, 0, 1, 2, 3, 8]
    """
    def __init__(self, a, b, channel=0):
        BaseOperation.__init__(self, channel)
        self.a = a
        self.b = b

    def munge(self, stream):
        a = self.a
        b = self.b
        s1 = stream[a]
        stream[a] = stream[b]
        stream[b] = s1

class StereoSwap(BaseOperation):
    """This swaps stereo channels by using two MonoSwaps.
    >>> s = StereoSwap(slice(0,4), slice(4,8))
    >>> data = [list(range(100)), list(range(100))]
    >>> s(data)
    >>> data[0][0:9]
    [4, 5, 6, 7, 0, 1, 2, 3, 8]
    >>> data[1][0:9]
    [4, 5, 6, 7, 0, 1, 2, 3, 8]
    """
    def __init__(self, a, b):
        BaseOperation.__init__(self, None)
        self &= MonoSwap(a, b, 0)
        self &= MonoSwap(a, b, 1)


if __name__ == '__main__':
    import doctest
    doctest.testmod()