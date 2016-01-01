import sys
import argparse
from . import load
from .randomizers import *
from . import operations as o

def build_arguments():
    parser = argparse.ArgumentParser(description="Mangle an audio file, using cut-up techniques based on dadaist and surrealist art.")
    parser.add_argument("input", metavar="input", type=str,
        help="the input file")
    parser.add_argument("output", metavar="output", nargs="?",
        help="the output file destination, defaults to output.wav",
        default="output.wav")
    parser.add_argument("--hpm", metavar="hpm", type=int, nargs="?",
        help="how many hits/cuts to make per minute.", default=180)
    return parser

def main():
    args = build_arguments().parse_args()

    inputfile = args.input
    outputfile = args.output
    hpm = args.hpm

    stream, rate = load.read(inputfile)
    stream = load.stereoify(stream)
    size = len(stream[0])

    hits = hpm * size / (rate*60)
    p = Population(o.__all__)
    for i in range(hits):
        op = p.get().generate(rate, size)
        op(stream)

    load.write(outputfile, stream, rate)

if __name__ == "__main__":
    main()