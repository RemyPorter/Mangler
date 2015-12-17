"""A slice factory that generates slices given an input stream."""

import random
from math import pi

def get_slice(frame_rate, stream_size, ratio=1.0):
    block = int(frame_rate * ratio)
    start = random.randint(0,stream_size-block-1)
    return slice(start, start+block)

def get_angle():
    return random.uniform(0, 2*pi)

def get_item(items):
    if isinstance(items, dict):
        return random.choice(items.items())[1]
    else:
        return random.choice(items)

def get_cuts(max=5):
    return random.randint(1,5)

def pick_channel():
    return random.randint(0,1)

def generated(slices, *args, **kwargs):
    """This decorator takes a number of expected slices,
    as well as arbitrary arguments. These arbitrary arguments
    must be no-parameter functions which generate values required
    for the generated initialization of an instance of the
    decorated class.

    >>> class Foo:
    ...   def __init__(self, a, garbage):
    ...      self.a = a
    ...      self.garbage = garbage
    >>> generated(1, lambda: "test")(Foo)
    >>> g = Foo.generate(1, 100)
    >>> g.garbage
    'test'
    """
    def wrapper(cls):
        def generate(cls, frame_rate, stream_size, ratio=1.0):
            s = [get_slice(frame_rate, stream_size, ratio) for i in range(slices)]
            s += map(lambda x: x(), args)
            kw = {k: v() for k,v in kwargs.items()}
            return cls(*s, **kw)
        cls.generate = classmethod(generate)
    return wrapper