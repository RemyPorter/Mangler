import sys
import argparse
from . import process

parser = argparse.ArgumentParser(description="Mangle an audio file, using cut-up techniques based on dadaist and surrealist art.")
parser.add_argument("input", metavar="input", type=str, help="the input file")
parser.add_argument("output", metavar="output", nargs="?", help="the output file destination, defaults to output.wav")
parser.add_argument("--hps", metavar="hps", type=int, nargs="?", help="the number of 'cuts' or 'hits' to make per second of audio, on average. Default is 3.")
args =parser.parse_args()
fname = args.input
oname = args.output
hps = args.hps
if hps is None:
    hps = 3
if oname is None:
    oname = "output.wav"
process(fname, oname, hps)