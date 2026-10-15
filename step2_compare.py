"""Step 2: compare the numbers directly. Exact matching finds nothing; sliding comparison is far too slow.
Results go to files/step2.json."""
import json
import time
import numpy as np
from songs import RATE, recording
from common import songs, the_clip, SONG, START, LENGTH

lib = songs()
song = lib[SONG]
i = int(START * RATE)
n = LENGTH * RATE


def as_int(x):                       # the whole numbers a sound file stores (16 bits)
    return np.round(np.clip(x, -1, 1) * 32767).astype(int)


clip = the_clip(lib)
quiet = recording(song, START, LENGTH, None, None)            # quieter, no noise at all
same_noisy = int(np.sum(as_int(song[i:i + n]) == as_int(clip)))
same_quiet = int(np.sum(as_int(song[i:i + n]) == as_int(quiet)))
print(f'equal samples at the right place: noisy clip {same_noisy} of {n:,}, quiet clip {same_quiet} of {n:,}')

# sliding: at every start position, multiply the clip by the song under it and add up
positions = len(song) - n + 1
work_song = positions * n
t0 = time.time()
trial = 2000
scores = [float(np.dot(song[p:p + n], clip)) for p in range(i - trial // 2, i + trial // 2)]
per_mult = (time.time() - t0) / (trial * n)
best = int(np.argmax(scores)) + i - trial // 2
print(f'best of {trial} positions near 12 s: sample {best} (right answer {i})')
song_s = work_song * per_mult
paper = 1_800_000
print(f'{positions:,} positions x {n:,} = {work_song:,} multiplications per song, {song_s:.1f} s per song')
print(f'100 songs: {100 * song_s / 60:.1f} min; 1.8 million songs: {paper * song_s / 86400:.0f} days')
json.dump({'n': n, 'same_noisy': same_noisy, 'same_quiet': same_quiet,
           'song_ints': as_int(song[i:i + 6]).tolist(), 'quiet_ints': as_int(quiet[:6]).tolist(),
           'clip_ints': as_int(clip[:6]).tolist(), 'positions': positions, 'work_song': work_song,
           'best': best, 'right': i, 'song_s': round(song_s, 2), 'lib_min': round(100 * song_s / 60, 1),
           'paper_days': round(paper * song_s / 86400), 'per_mult_ns': round(per_mult * 1e9, 3)},
          open('files/step2.json', 'w'), indent=1)
