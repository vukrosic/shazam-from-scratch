"""Shazam from scratch: spectrogram, peaks, pair hashes and offset votes.

The method is Avery Wang's 2003 paper "An Industrial-Strength Audio Search Algorithm".
The settings below are ours; the paper does not give its exact numbers."""
from collections import defaultdict
import numpy as np

WINDOW = 1024        # samples per slice: 1024 / 8000 = 0.128 s
HOP = 256            # a new slice every 256 samples = 0.032 s
PEAK_TIME = 8        # a peak is the loudest point within 8 slices before and after it
PEAK_FREQ = 16       # and within 16 frequency rows above and below it
LOUD = 0.5           # and at least 10 ** 0.5 = 3.2 times stronger than the typical point
FAN_OUT = 10         # every anchor peak is paired with this many later peaks (the paper's example)
ZONE_START = 1       # the target zone starts 1 slice after the anchor
ZONE_END = 40        # and ends 40 slices after it (1.28 s)
ZONE_FREQ = 120      # and reaches 120 rows above and below it
MIN_SCORE = 12       # fewer lined-up votes than this: answer "no match"


def dft(x):
    """The slow way, straight from the definition: one sum per frequency."""
    n = len(x)
    k = np.arange(n)
    return np.array([np.sum(x * np.exp(-2j * np.pi * f * k / n)) for f in range(n)])


def fft(x):
    """The fast way: split into even and odd samples, solve both halves, join them.
    Works on the last axis, so it can do many slices at once. Length must be a power of two."""
    n = x.shape[-1]
    if n == 1:
        return x.astype(complex)
    even = fft(x[..., 0::2])
    odd = fft(x[..., 1::2])
    turn = np.exp(-2j * np.pi * np.arange(n // 2) / n) * odd
    return np.concatenate([even + turn, even - turn], axis=-1)


def spectrogram(samples):
    """Rows = frequency, columns = time. Each value: how strong that frequency is in that slice."""
    count = 1 + (len(samples) - WINDOW) // HOP
    idx = np.arange(WINDOW)[None, :] + HOP * np.arange(count)[:, None]
    slices = samples[idx] * np.hanning(WINDOW)
    strength = np.abs(fft(slices))[:, :WINDOW // 2]
    return np.log10(strength + 1e-6).T          # shape (512 rows, count columns)


def bin_hz(row):
    return row * 8000 / WINDOW


def slice_s(col):
    return col * HOP / 8000


def max_around(spec, dt=PEAK_TIME, df=PEAK_FREQ):
    """For every point, the largest value in the box around it (rows +-df, columns +-dt)."""
    big = spec.copy()
    pad = np.pad(spec, ((df, df), (0, 0)), constant_values=-np.inf)
    for s in range(2 * df + 1):
        big = np.maximum(big, pad[s:s + spec.shape[0], :])
    out = big.copy()
    pad = np.pad(big, ((0, 0), (dt, dt)), constant_values=-np.inf)
    for s in range(2 * dt + 1):
        out = np.maximum(out, pad[:, s:s + spec.shape[1]])
    return out


def peaks(spec):
    """Points louder than everything near them, and above the typical level. Returns (column, row) pairs."""
    loud = spec > np.median(spec) + LOUD
    is_peak = (spec == max_around(spec)) & loud
    rows, cols = np.nonzero(is_peak)
    order = np.lexsort((rows, cols))
    return [(int(cols[i]), int(rows[i])) for i in order]


def pack(f1, f2, dt):
    """Two frequency rows (9 bits each) and a time gap (6 bits) in one whole number."""
    return (f1 << 15) | (f2 << 6) | dt


def unpack(h):
    return h >> 15, (h >> 6) & 511, h & 63


def hashes(points, fan_out=FAN_OUT):
    """Pair every anchor peak with the next few peaks in its target zone. Returns (hash, anchor column)."""
    out = []
    for i, (t1, f1) in enumerate(points):
        taken = 0
        for t2, f2 in points[i + 1:]:
            dt = t2 - t1
            if dt > ZONE_END:
                break
            if dt < ZONE_START or abs(f2 - f1) > ZONE_FREQ:
                continue
            out.append((pack(f1, f2, dt), t1))
            taken += 1
            if taken == fan_out:
                break
    return out


def fingerprint(samples):
    return hashes(peaks(spectrogram(samples)))


class Index:
    """The database: hash -> every (song, column) where that hash appears."""

    def __init__(self):
        self.table = defaultdict(list)
        self.songs = 0
        self.entries = 0

    def add(self, song_id, samples):
        for h, t in fingerprint(samples):
            self.table[h].append((song_id, t))
            self.entries += 1
        self.songs += 1

    def votes(self, samples):
        """For every hash of the clip found in the table, one vote for (song, song column - clip column)."""
        count = defaultdict(int)
        for h, t in fingerprint(samples):
            for song_id, ts in self.table.get(h, ()):
                count[(song_id, ts - t)] += 1
        return count

    def search(self, samples):
        """Best (score, song, offset in columns) for every song, best first."""
        best = {}
        for (song_id, off), n in self.votes(samples).items():
            if n > best.get(song_id, (0, 0))[0]:
                best[song_id] = (n, off)
        return sorted(((n, s, off) for s, (n, off) in best.items()), reverse=True)

    def answer(self, samples):
        """The song, or None when the best song has too few lined-up votes."""
        best = self.search(samples)
        return best[0][1] if best and best[0][0] >= MIN_SCORE else None
