from . import load
from . import analyzer

def process(filename, outputfile, hits_per_minute=180, limit=None, ops=None):
    channels,frame_rate = load.read(filename, limit)
    target = frame_rate
    hits = hits_per_minute * len(channels[0])/(target*60)
    data = analyzer.mangle(channels, num_hits=hits, block_size=target, ops=ops)
    load.write(outputfile, channels, frame_rate)