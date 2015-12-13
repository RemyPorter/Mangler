import numpy as np
import random
from scipy import ndimage
from functools import partial

def combine(*args):
    def f(chan, start, end, block_size=None):
        res = chan
        for a in args:
            res = a(res, start, end, block_size)
        return res
    return f

def get_range(size, block_size):
    s = random.randint(0,size-block_size-1)
    return s, s+block_size

def rotate(chan, start, end, block_size=None):
    chan[start:end] = map(
        lambda x: -1 * x, chan[start:end])
    return chan

def flip(chan, start, end, block_size=None):
    chan[start:end] = list(reversed(chan[start:end]))
    return chan

def swap(chan, start, end, block_size=50):
    xstart, xend = get_range(len(chan), block_size)
    temp = chan[start:end]
    chan[start:end] = chan[xstart:xend]
    chan[xstart:xend] = temp
    return chan

def dup(chan, start, end, block_size):
    xs, xe = get_range(len(chan), block_size)
    chan[xs:xe] = chan[start:end]
    return chan

def convolve(chan, start, end, block_size, kernel):
    chan[start:end] = ndimage.convolve(chan[start:end], kernel)
    return chan

def stutter(chan, start, end, block_size):
    cut_up = block_size / 4
    cut_s, cut_e = get_range(start, cut_up)
    cut = list(chan[cut_s:cut_e])
    chan[start:end] = cut*4
    return chan

blur = [0.04] * int(1.0/0.04)
soft = [0.005] * int(1.0/0.005)
ramp = [1,1,1,1,1,0,0,0,0,-1,-1,-1,-1,-1]

e1 = partial(convolve, kernel=[-1, 2, -1])
e2 = partial(convolve, kernel=[-1, -1, 4, -1, -1])
bl = partial(convolve, kernel=blur)
sf = partial(convolve, kernel=soft)
r = partial(convolve, kernel=ramp)

stutterAndFlip = combine(stutter, flip)
reverseBlurReverse = combine(flip, bl, flip)
dupFlip = combine(dup, flip)

ops = [swap, swap, swap, swap,swap,
        flip, flip, flip, flip,
        dup, dup, dup, dup, dup,
        stutter, stutter, stutter,
        e1, e2, bl, sf, r,
        e1, e2, bl, sf,
        stutterAndFlip, stutterAndFlip,
        reverseBlurReverse, reverseBlurReverse,
        dupFlip, dupFlip,
        rotate, rotate, rotate
    ]


def fft(channels):
    return np.fft.fft2(channels)

def ifft(data):
    return np.fft.ifft2(data)

def hit(data, length, block_size):
    coin = random.randint(0,1)
    chan = data[coin]
    start,end = get_range(len(chan), block_size)
    op = random.choice(ops)
    #op = flip
    chan = op(chan, start, end, block_size)
    data[coin] = chan
    return data

def _clean(channel):
    return map(lambda x: int(x.real), channel)

def mangle(channels, block_size=50, num_hits=1000, dtype=np.int16):
    print("About to FFT")
    data = channels
    print("FFT complete")
    maxx = len(data[0]) - block_size
    for i in range(num_hits):
        print "Hitting..." + str(i)
        data = hit(data, maxx, block_size)
    print "Done hitting..."
    new_channels = data
    return np.array(new_channels, dtype=dtype)

