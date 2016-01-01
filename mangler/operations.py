"""The objects in this module represent a series of operations
which can be performed against an array of samples. These
samples could theoretically be anything, but the core purpose
is audio data. All of these operations support multi-channel
audio as their core input, but may only operate on one channel, if
they desire.

All of these have the generated decorator applied, which injects a
generate method into each class definition, which creates a
randomized instance.

>>> s = Swap.generate(1, 100)
>>> isinstance(s.a, slice)
True
>>> data = test_data()
>>> s(data)
>>> for op in __all__:
...   o = op.generate(1,100)
...   o(data)
"""

import random
from numpy.fft import fft, ifft, fft2, ifft2, rfft,irfft
import numpy as np
from scipy.ndimage import convolve
from math import atan2, pi, hypot, cos, sin
from functools import partial
from .randomizers import *

kernels = {
    "blur": [0.04 * (int(1.0/0.04))],
    "sharpen": [-3, 7, -3],
    "edge": [-1, 2, -1],
    "edge1": [-1, -1, 4, -1, -1],
    "neighborhood": [1, 1, -4, 1, 1]
}

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
generated(2, pick_channel)(Swap)

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
generated(1, pick_channel)(Invert)

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
generated(1, pick_channel)(Reverse)

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
generated(2, pick_channel)(Dup)

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
generated(1, partial(get_item, kernels))(Convolution)

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
generated(1, get_angle, pick_channel)(Rotate)

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
        size = int(round(len(full) / float(self.stutters)))
        cut = list(full[0:size]) * self.stutters
        stream[s] = cut[0:len(full)]
generated(1, get_cuts, pick_channel)(Stutter)

class FrameSmear(OnePointOp):
    """Take a slice `s` and replace each frame
    with a rolling average of the frames seen so far.

    >>> s = FrameSmear(slice(0,4))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:4]
    [0, 0, 1, 1]
    """
    def __init__(self, s, channel=0):
        OnePointOp.__init__(self, s, channel)

    def munge(self, stream):
        total,count = 0,0
        sl = stream[self.slice]
        for i,v in enumerate(sl):
            total += v
            count += 1
            sl[i] = total / count
        stream[self.slice] = sl
generated(1, pick_channel)(FrameSmear)

class Merge(TwoPointOp):
    """Take slice `b` and add it to slice `a`, after applying
    a ratio.

    >>> s = Merge(slice(0,4), slice(4,8), 0.75)
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:4]
    [3, 4, 6, 8]
    """
    def __init__(self, a, b, ratio=1.0, channel=0):
        TwoPointOp.__init__(self, a, b, channel)
        self.ratio = ratio

    def munge(self, stream):
        st = np.array(stream)
        st[self.a] += np.array((st[self.b] * self.ratio), dtype=np.int16)
        stream[self.a] = st[self.a]
generated(2, pick_channel)(Merge)

class FlipStereo(OnePointOp):
    """Flip the two stereo channels.
    >>> s = FlipStereo(slice(0,4))
    >>> data = test_data()
    >>> data[1][0:4] = [10, 9, 8, 7]
    >>> s(data)
    >>> data[0][0:4]
    [10, 9, 8, 7]
    >>> data[1][0:4]
    [0, 1, 2, 3]
    """
    def __init__(self, s, channel=None):
        OnePointOp.__init__(self, s, None)

    def munge(self, stream):
        s = self.slice
        orig = stream[0][s]
        stream[0][s] = stream[1][s]
        stream[1][s] = orig
generated(1)(FlipStereo)

class InterleaveStereo(OnePointOp):
    """Swap stereo channels on every alternate sample.
    >>> s = InterleaveStereo(slice(0,4))
    >>> data = test_data()
    >>> data[1][0:4] = [10, 9, 8, 7]
    >>> s(data)
    >>> data[0][0:4]
    [10, 1, 8, 3]
    >>> data[1][0:4]
    [0, 9, 2, 7]
    """
    def __init__(self, s, channel=None):
        OnePointOp.__init__(self, s, None)

    def munge(self, stream):
        s = self.slice
        zipped = zip(stream[0][s], stream[1][s])
        left = []
        right = []
        for i,z in enumerate(zipped):
            if i % 2 == 0:
                right.append(z[1])
                left.append(z[0])
            else:
                right.append(z[0])
                left.append(z[1])
        stream[1][s] = left
        stream[0][s] = right
generated(1)(InterleaveStereo)

class Expand(OnePointOp):
    """
    Find the average frequency in the range, then examine
    each sample and find its diffence from that frequency-
    and double that difference.

    >>> s = Expand(slice(0,4))
    >>> data = test_data()
    >>> s(data)
    >>> data[0][0:4]
    [0, 2, 3, 5]
    """
    def __init__(self, s, channel=0):
        OnePointOp.__init__(self, s, channel)

    def munge(self, stream):
        s = self.slice
        ft = rfft(stream[s])
        assert(len(ft) > 0)
        avg = reduce(lambda acc, elem: acc + elem, ft) / len(ft)
        harmonics = np.arange(len(ft))
        for i,m in enumerate(ft):
            diff = m - avg
            ft[i] += diff
        stream[s] = _clean(irfft(ft))
generated(1)(Expand)

__all__ = [Swap, Invert,
    Reverse, Dup, Convolution,
    Rotate, FrameSmear, Merge, Stutter,
    FlipStereo, InterleaveStereo, Expand]

if __name__ == '__main__':
    def test_data():
        return [list(range(100)), list(range(100))]
    import doctest
    doctest.testmod()