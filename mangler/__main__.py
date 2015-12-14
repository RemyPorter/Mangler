import sys
import argparse
from . import process

parser = argparse.ArgumentParser(description="Mangle an audio file, using cut-up techniques based on dadaist and surrealist art.")
parser.add_argument("input", metavar="input", type=str, help="the input file")
parser.add_argument("output", metavar="output", nargs="?", help="the output file destination, defaults to output.wav")
parser.add_argument("--hpm", metavar="hpm", type=int, nargs="?", help="the number of 'cuts' or 'hits' to make per minute of audio, on average. Default is 180, or 3 hits per second.")
args =parser.parse_args()
fname = args.input
oname = args.output
hpm = args.hpm
if hpm is None:
    hpm = 180
if oname is None:
    oname = "output.wav"
process(fname, oname, hpm)