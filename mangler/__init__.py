from . import load
from . import analyzer

def process(filename, limit=None):
    channels,frame_rate = load.read(filename, limit)
    target = frame_rate
    hits = 4 * len(channels[0])/target
    data = analyzer.mangle(channels, num_hits=hits, block_size=target)
    print "Writing..."
    load.write("output.wav", channels, frame_rate)