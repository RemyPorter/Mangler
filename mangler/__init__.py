from . import load
from . import analyzer

def process(filename, outputfile, hits_per_second=3, limit=None):
    channels,frame_rate = load.read(filename, limit)
    target = frame_rate
    hits = hits_per_second * len(channels[0])/target
    data = analyzer.mangle(channels, num_hits=hits, block_size=target)
    load.write(outputfile, channels, frame_rate)