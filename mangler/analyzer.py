import numpy as np
import random
from scipy import ndimage
from functools import partial
from numpy.fft import fft, ifft
from math import atan2, sin, cos, hypot, pi

def compose(*args):
    def f(chan, start, end, block_size=None):
        res = chan
        for a in args:
            res = a(res, start, end, block_size)
        return res
    return f

def get_range(size, block_size):
    s = random.randint(0,size-block_size-1)
    return s, s+block_size

def rotate(chan, start, end, block_size):
    amt = random.random() * 2
    def rt(cpx, amount_in_radians=amt):
        angle = atan2(cpx.real, cpx.imag) + amount_in_radians
        r = hypot(cpx.real, cpx.imag)
        return complex(r * cos(angle), r * sin(angle))
    mapped = map(rt, fft(chan[start:end]))
    chan[start:end] = _clean(ifft(mapped))
    return chan

def invert(chan, start, end, block_size=None):
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

def frame_smear(chan, start, end, block_size):
    segment = chan[start:end]
    count = 0
    res = []
    for s in segment:
        if count % 4 == 0:
            res.append(s)
        else:
            res.append(res[-1])
        count += 1
    chan[start:end] = res
    return chan

blur = [0.04] * int(1.0/0.04)
soft = [0.005] * int(1.0/0.005)
ramp = [1,1,1,1,1,0,0,0,0,-1,-1,-1,-1,-1]

e1 = partial(convolve, kernel=[-1, 2, -1])
e2 = partial(convolve, kernel=[-1, -1, 4, -1, -1])
e3 = partial(convolve, kernel=[-1, 4, -3])
bl = partial(convolve, kernel=blur)
sf = partial(convolve, kernel=soft)
r = partial(convolve, kernel=ramp)

stutterAndFlip = compose(stutter, flip)
reverseBlurReverse = compose(flip, bl, flip)
dupFlip = compose(dup, flip)

coreOps = {
    swap: (10, 0),
    flip: (10, 0),
    dup: (6, 0),
    stutter: (6, 0),
    e1: (1, 1),
    e2: (1, 1),
    e3: (1, 1),
    bl: (5, 1),
    sf: (4, 1),
    stutterAndFlip: (2, 0),
    reverseBlurReverse: (1, 0),
    dupFlip: (5, 0),
    invert: (3, 0),
    frame_smear: (4, 0),
    rotate: (8, 0)
}

def fftwrap(func):
    def wrapped(chan, start, end, block_size):
        f = fft(chan)
        res = func(f, start, end, block_size)
        return clean(ifft(res))
    return wrapped

def get_ops(coreOps):
    res = []
    for f in coreOps.keys():
        res += [f]*coreOps[f][0]
        res += [f]*coreOps[f][1]
    return res

ops = get_ops(coreOps)


def hit(data, length, block_size):
    coin = random.randint(0,len(data)-1)
    chan = data[coin]
    start,end = get_range(len(chan), block_size)
    op = random.choice(ops)
    #op = flip
    chan = op(chan, start, end, block_size)
    data[coin] = chan
    return data

def _clean(channel):
    return map(lambda x: int(x.real), channel)

def mangle(channels, block_size=50, num_hits=1000, dtype=np.int16, ops=None):
    data = channels
    maxx = len(data[0]) - block_size
    for i in range(num_hits):
        data = hit(data, maxx, block_size)
    new_channels = data
    return np.array(new_channels, dtype=dtype)

