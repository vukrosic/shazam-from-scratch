"""Step 7: the full test. Clips of 1 to 10 seconds, from no noise to noise three times louder than the music.
Counts right answers, "no match" answers and wrong answers. Results go to files/step7.json."""
import json
import numpy as np
from songs import make_song, recording
from common import songs, index, test_clips

lib = songs()
idx = index(lib)
LENGTHS = [1, 2, 3, 5, 10]
NOISES = [None, 0, -3, -6, -9]
N = 40
grid = []
for length in LENGTHS:
    for snr in NOISES:
        right = none = wrong = 0
        for k, clip in test_clips(lib, N, length, snr, seed=100 + length * 10 + (snr or 1)):
            a = idx.answer(clip)
            right += a == k
            none += a is None
            wrong += a is not None and a != k
        grid.append({'length': length, 'snr': snr, 'right': right, 'none': none, 'wrong': wrong})
        print(f'{length:>2} s, noise {str(snr):>4} dB: right {right:>2}/{N}, no match {none:>2}, wrong {wrong}')
rng = np.random.default_rng(9)
strangers = [idx.answer(recording(make_song(7000 + j)[0], 5, 5, 0, rng)) for j in range(100)]
false = sum(a is not None for a in strangers)
print(f'100 songs that are not in the library: {false} wrongly named')
json.dump({'n': N, 'lengths': LENGTHS, 'noises': NOISES, 'grid': grid, 'strangers': 100, 'false': false},
          open('files/step7.json', 'w'), indent=1)
