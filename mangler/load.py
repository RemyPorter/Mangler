import os
import numpy as np
from pydub import AudioSegment
import wave

def _read_pydub(filename, limit=None):
    """Read a file using pydub"""
    audio_file = AudioSegment.from_file(filename)
    if limit:
        audio_file = audio_file[:1000*limit]
    data = np.fromstring(audio_file._data, np.int16)
    channels = []
    for channel in xrange(audio_file.channels):
        channels.append(data[channel::audio_file.channels])
    return channels, audio_file.frame_rate

def _read_wavio(filename, limit=None):
    """Read a file using wavio, only for 24-bit wav files."""
    fs, _, audio_file = wavio.readwav(filename)
    if limit:
        audiofile = audiofile[:limit * 1000]
    audio_file = audio_file.T
    audio_file = audio_file.astype(np.int16)
    channels = []
    for chn in audiofile:
        channels.append(chn)
    return channels, audio_file.frame_rate

def read(filename, limit=None):
    """Read an audio file in. Try pydub, and if that fails
    fallback onto wavio."""
    try:
        return _read_pydub(filename, limit)
    except:
        return _read_wavio(filename, limit)

def write(filename, channels, rate):
    w = wave.open(filename, "wb")
    w.setnchannels(len(channels))
    w.setframerate(rate)
    w.setsampwidth(2)
    combined = np.array(channels).T
    w.writeframes(combined.tobytes())
    w.close()

def stereoify(stream):
    if len(stream) > 1:
        return stream
    return [stream[0], stream[0]]