"""The objects in this module represent a series of operations
which can be performed against an array of samples. These
samples could theoretically be anything, but the core purpose
is audio data. All of these operations support multi-channel
audio as their core input, but may only operate on one channel, if
they desire."""

import random
from numpy.fft import fft, ifft, fft2, ifft2
from scipy.ndimage import convolve
from math import atan2, pi, hypot, cos, sin

def _clean(channel):
    """Map a list of complex numbers to their real components."""
    return map(lambda x: int(x.real), channel)

class BaseOperation(object):
    """A base class which represents a chain of operations.
    This is essentially a singly-linked list, done this way
    to make it easy to chain operations together with a fluent
    syntax.

    >>> bop1 = BaseOperation()
    >>> bop1 &= BaseOperation()
    >>> bop1.next_op
    <BaseOperation>
    >>> bop1([], True)
    Testing
    Testing
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

    def __call__(self, stream, test=False):
        if test:
            print "Testing"
        if not self.channel is None:
            self.munge(stream[self.channel])
        else:
            self.munge(stream)
        if self.next_op:
            self.next_op(stream, test)

    def __repr__(self):
        return "<BaseOperation>"

    def munge(self, stream):
        pass

class OnePointOp(BaseOperation):
    """An operation that works on a single slice 's'."""
    def __init__(self, s, channel=None):
        BaseOperation.__init__(self, channel)
        self.slice = s

class TwoPointOp(BaseOperation):
    """An operation that modifies two slices in tandem, 'a' and 'b'"""
    def __init__(self, a, b, channel=None):
        BaseOperation.__init__(self, channel)
        self.a = a
        self.b = b

class Stereo(type):
    def __init__(cls, name, bases, nmspc):
        orig = cls.__init__
        def innernit(self, *args):
            orig(self, *args)
            for b in bases:
                self &= b(*args, channel=1)
        cls.__init__ = innernit

class Swap(TwoPointOp):
    """This swap operation grabs two segments on a single channel
    and swaps them.

    >>> s = Swap(slice(0,4), slice(4,8)) & Swap(slice(0,2), slice(2,4))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:9]
    [6, 7, 4, 5, 0, 1, 2, 3, 8]
    """
    def __init__(self, a, b, channel=0):
        TwoPointOp.__init__(self, a, b, channel)

    def munge(self, stream):
        a = self.a
        b = self.b
        s1 = stream[a]
        stream[a] = stream[b]
        stream[b] = s1

class StereoSwap(Swap):
    """This swaps stereo channels by using two Swaps.
    >>> s = StereoSwap(slice(0,4), slice(4,8))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:9]
    [4, 5, 6, 7, 0, 1, 2, 3, 8]
    >>> data[1][0:9]
    [4, 5, 6, 7, 0, 1, 2, 3, 8]
    """
    __metaclass__ = Stereo
    # def __init__(self, a, b):
    #     BaseOperation.__init__(self, None)
    #     self &= Swap(a, b, 0)
    #     self &= Swap(a, b, 1)

class Invert(OnePointOp):
    """Inverts the samples on a channel, ie, multiply by -1

    >>> s = Invert(slice(0,4))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:4]
    [0, -1, -2, -3]
    """
    def __init__(self, s, channel=0):
        OnePointOp.__init__(self, s, channel)

    def munge(self, stream):
        stream[self.slice] = map(lambda x: x * -1, stream[self.slice])

class StereoInvert(Invert):
    """Inverts the sample on two channels."""
    __metaclass__ = Stereo

class Reverse(OnePointOp):
    """Reverses a section of audio on one channel.

    >>> s = Reverse(slice(0,4))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:4]
    [3, 2, 1, 0]
    """
    def __init__(self, s, channel=0):
        OnePointOp.__init__(self, s, channel)

    def munge(self, stream):
        s = self.slice
        stream[s] = list(reversed(stream[s]))

class StereoReverse(BaseOperation):
    """Reverses a section in both channels."""
    __metaclass__ = Stereo

class Dup(TwoPointOp):
    """Duplicate a source over a destination on a single channel.

    >>> s = Dup(slice(0,4), slice(4,8))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:9]
    [0, 1, 2, 3, 0, 1, 2, 3, 8]
    """
    def __init__(self, a, b, channel=0):
        TwoPointOp.__init__(self, a, b, channel)

    def munge(self, stream):
        a = self.a
        b = self.b
        stream[b] = stream[a]

class StereoDup(Dup):
    """Duplicate a source over a destination on both channels."""
    __metaclass__ = Stereo

class Convolution(OnePointOp):
    """Perform a convolution on a single channel of the stream,
    through the slice 's'.

    >>> s = Convolution(slice(0,50), [-1, 2, 0])
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:10]
    [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    """
    def __init__(self, s, kernel, channel=0):
        OnePointOp.__init__(self, s, channel)
        self.kernel = kernel

    def munge(self, stream):
        s = self.slice
        stream[s] = convolve(stream[s], self.kernel)

class Rotate(OnePointOp):
    """Perform an FFT on a single channel, rotate all
    of those points through the complex plane by some deflection angle,
    and then convert back into the original data.

    Deflection is in radians.

    >>> s = Rotate(slice(0,10), 3*pi/2)
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:12]
    [0, 8, 8, 7, 5, 5, 4, 3, 1, 0, 10, 11]
    """
    def __init__(self, s, deflection, channel=0):
        OnePointOp.__init__(self, s, channel)
        self.deflection = deflection

    def munge(self, stream):
        s = self.slice
        f = fft(stream[s])
        defl = self.deflection
        def rotate(cpx, defl=defl):
            angle = atan2(cpx.real, cpx.imag) + defl
            r = hypot(cpx.real, cpx.imag)
            return complex(r * cos(angle), r * sin(angle))
        f = map(rotate, f)
        stream[s] = _clean(ifft(f))

class Stutter(OnePointOp):
    """Take a slice 's', extract a fragment of that slice,
        and repeat that fragment for a `cuts` number of times
        out to the length of the original slice.

        >>> s = Stutter(slice(0,4), 4)
        >>> data = test_data()
        >>> s(data)
        >>> data[0][0:4]
        [0, 0, 0, 0]
    """
    def __init__(self, s, cuts, channel=0):
        OnePointOp.__init__(self, s, channel)
        self.stutters = cuts

    def munge(self, stream):
        s = self.slice
        full = stream[s]
        size = len(full) / self.stutters
        cut = full[0:size] * self.stutters
        stream[s] = cut[0:len(full)]



if __name__ == '__main__':
    def test_data():
        return [list(range(100)), list(range(100))]
    import doctest
    doctest.testmod()