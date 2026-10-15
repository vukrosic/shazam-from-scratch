"""Shared setup: the library of 100 songs, the one recording the film follows, and the test clips."""
import os
import pickle
import numpy as np
from songs import library, recording, RATE
from shazam import Index, HOP

SONGS = 100          # songs 1..100 in the library
SONG = 17            # the song playing in the room
START = 12.0         # the phone starts listening 12 seconds into it
LENGTH = 5           # for 5 seconds
SNR = 0              # room noise as loud as the music (0 dB)
START_COL = int(START * RATE) // HOP     # 375: the slice where the clip starts


def songs():
    return library(SONGS)


def the_clip(lib, snr=SNR):
    return recording(lib[SONG], START, LENGTH, snr, np.random.default_rng(2026))


def index(lib):
    """Fingerprints of all 100 songs, saved after the first build."""
    path = 'files/index.pkl'
    if os.path.exists(path):
        return pickle.load(open(path, 'rb'))
    idx = Index()
    for k, s in lib.items():
        idx.add(k, s)
    pickle.dump(idx, open(path, 'wb'))
    return idx


def test_clips(lib, n=20, length=LENGTH, snr=SNR, seed=7):
    """n recordings of random songs at random places: (true song, samples)."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        k = int(rng.integers(1, SONGS + 1))
        start = float(rng.uniform(0, 30 - length - 0.5))
        out.append((k, recording(lib[k], start, length, snr, rng)))
    return out
