#The Cut Up
This program applies various cut-up techniques to create a collage from a given input file. It randomly selects from a pool of different operations and applies them to an input audio file.

It uses FFMPEG for loading the audio (through PyDub), so it can handle pretty much any input file. For the moment, I'm only using the `wave` module to generate output, so it can only output a WAV file. This is something I'll definitely fix.

The input audio needs to be at least 2 channels. If it contains more channels, only the first two channels will be modified.

# Running It
`python2.7 INPUTFILE OUTPUTFILE [--hpm 180]`

The `--hpm` flag controls how many "hits per minute", which defaults to 180, which is the same as 3 hits per second. Set this parameter to control how glitchy the output is. More hits means more glitches.

# TODO
I want to add a CLI option which allows you to specify the weighting of the population. The underlying logic is there, it just needs a user interface.

After that, the next big thing is going to be adding compressed output, which once again, will probably use FFMPEG.