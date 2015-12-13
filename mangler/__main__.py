import sys
import argparse
from . import process

parser = argparse.ArgumentParser(description="Mangle an audio file, using cut-up techniques based on dadaist and surrealist art.")
parser.add_argument("input", metavar="input", type=str, help="the input file")
parser.add_argument("output", metavar="output", nargs="?", help="the output file destination, defaults to output.wav")
args =parser.parse_args()
fname = args.input
oname = args.output
if oname is None:
    oname = "output.wav"
process(fname, oname)