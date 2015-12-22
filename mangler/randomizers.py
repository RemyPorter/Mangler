"""A slice factory that generates slices given an input stream."""

import random
from math import pi
from collections import OrderedDict

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

class Population(object):
    """Build a weighted population that can
    return random items based on that probability.

    >>> p = Population(opts, Swap=0.5, Merge=0.5)
    >>> p._get(0.45)
    'Merge'
    >>> p._get(0.55)
    'Swap'
    >>> p._object("Swap") is Swap
    True
    >>> p._object("Invert") is Invert
    True
    >>> p2 = Population(opts)
    >>> p2._get(0.45)
    'Dup'
    >>> p2._get(0.24)
    'Invert'
    >>> p2._get(0.92)
    'Merge'
    >>> s = p2._object(p2._get(0.24)).generate(1, 100)
    >>> isinstance(s, Invert)
    True
    """
    def __init__(self, options, **kwargs):
        self._options = options
        self.overrides = kwargs
        self.prob_total = 1.0
        self.probs = OrderedDict()
        self.build_probs()

    def build_probs(self):
        allocated = 0
        unused = map(lambda x: x.__name__, self._options)
        prob = self.prob_total
        for k,v in self.overrides.items():
            allocated += v
            self.probs[allocated] = k
            unused.remove(k)
        if allocated >= prob:
            return

        remaining = (prob - allocated) / float(len(unused))
        for i in unused:
            allocated += remaining
            self.probs[allocated] = i

    def _get(self, value):
        r = value
        for k in self.probs.keys():
            if r < k:
                return self.probs[k]
        return self.probs.values()[-1]

    def _object(self, key):
        i = map(lambda x: x.__name__, self._options).index(key)
        return self._options[i]

    def get(self):
        s = self._get(random.random())
        return self._object(s)


if __name__ == "__main__":
    import doctest
    from .operations import __all__ as opts
    from .operations import Swap, Invert
    doctest.testmod()
