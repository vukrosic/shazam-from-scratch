"""Step 4: keep only the peaks (the stars of the constellation map), check they survive noise,
then slide the clip's stars over each song's stars. Results go to files/step4.json."""
import json
import time
import numpy as np
from shazam import spectrogram, peaks
from common import songs, the_clip, test_clips, SONG, START_COL, LENGTH
from songs import RATE
from shazam import HOP

lib = songs()
song_pk = {k: peaks(spectrogram(s)) for k, s in lib.items()}
mine = song_pk[SONG]
print(f'song {SONG}: {len(mine)} peaks in 30 s = {len(mine) / 30:.0f} per second '
      f'(out of {512 * 934:,} points in the spectrogram)')
width = LENGTH * RATE // HOP - 3                       # slices fully inside the 5 s clip
span = {(t - START_COL, f) for t, f in mine if START_COL <= t < START_COL + width}


def survive(clip):
    got = {(t, f) for t, f in peaks(spectrogram(clip)) if t < width}
    near = len(span & got)                                 # same slice, same row exactly
    return len(got), near / len(span)


survival = []
for snr in [None, 0, -3, -6, -9]:
    n, frac = survive(the_clip(lib, snr))
    survival.append({'snr': snr, 'clip_peaks': n, 'kept': round(frac, 3)})
    print(f'noise {snr} dB: clip has {n} peaks, {frac:.0%} of the song peaks are still there')

clip_pk = peaks(spectrogram(the_clip(lib)))


def slide(cpk, spk):
    """For every shift, how many clip stars land on a song star. Returns the counts."""
    stars = set(spk)
    last = max(t for t, _ in spk) if spk else 0
    return [sum((t + s, f) in stars for t, f in cpk) for s in range(last + 1)]


curve = slide(clip_pk, mine)
best_shift = int(np.argmax(curve))
print(f'slide over song {SONG}: best shift {best_shift} slices = {best_shift * HOP / RATE:.2f} s, '
      f'{curve[best_shift]} stars line up; typical shift {np.median(curve):.0f}')
t0 = time.time()
tops = {k: max(slide(clip_pk, p)) for k, p in song_pk.items()}
t_slide = time.time() - t0
rank = sorted(tops.items(), key=lambda kv: -kv[1])[:5]
print(f'slide over all 100 songs: {t_slide:.1f} s, best songs', rank)
paper_h = t_slide / 100 * 1_800_000 / 3600
print(f'at that speed, 1.8 million songs: {paper_h:.1f} hours per question')

named = 0
for k, clip in test_clips(lib):
    cpk = peaks(spectrogram(clip))
    named += max(song_pk, key=lambda s: max(slide(cpk, song_pk[s]))) == k
print(f'test: {named} of 20 clips named correctly by sliding stars')
json.dump({'song_peaks': len(mine), 'per_s': round(len(mine) / 30), 'points': 512 * 934,
           'song_stars': sorted([[t, f] for t, f in span]), 'clip_stars': [[t, f] for t, f in clip_pk],
           'survival': survival, 'curve': curve, 'best_shift': best_shift, 'best_s': best_shift * HOP / RATE,
           'best_count': curve[best_shift], 'typical': float(np.median(curve)), 't_slide': round(t_slide, 1),
           'rank': rank, 'named': named, 'paper_h': round(paper_h, 1)},
          open('files/step4.json', 'w'), indent=1)
