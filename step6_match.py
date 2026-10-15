"""Step 6: look up every hash of the clip and let each hit vote for (song, time difference).
The right song gets a tall spike at one time difference. Results go to files/step6.json."""
import json
import time
from collections import Counter
import numpy as np
from shazam import fingerprint, MIN_SCORE, HOP
from songs import RATE, make_song, recording
from common import songs, the_clip, index, test_clips, SONG

lib = songs()
idx = index(lib)
clip = the_clip(lib)
ch = fingerprint(clip)
found = [(h, t) for h, t in ch if h in idx.table]
votes = idx.votes(clip)
print(f'clip: {len(ch)} hashes, {len(found)} found in the table, {sum(votes.values())} votes')
best = idx.search(clip)
for n, s, off in best[:5]:
    print(f'  song {s}: {n} votes at a difference of {off} slices ({off * HOP / RATE:.2f} s)')
# the first few votes, written out
rows = []
for h, t in found[:6]:
    for s, ts in idx.table[h][:2]:
        rows.append({'hash': h, 'clip_t': t, 'song': s, 'song_t': ts, 'diff': ts - t})
hist = Counter()
for (s, off), n in votes.items():
    if s == SONG:
        hist[off] += n
runner = best[1][1]
hist2 = Counter({off: n for (s, off), n in votes.items() if s == runner})
print(f'song {SONG}: votes spread over {len(hist)} differences, tallest {max(hist.values())}; '
      f'song {runner}: tallest {max(hist2.values())}')
t0 = time.time()
for _ in range(20):
    idx.search(clip)
ms = (time.time() - t0) / 20 * 1000
print(f'one search over 100 songs: {ms:.0f} ms (fingerprint of the clip included)')

stranger, _ = make_song(5000)                 # a song that is not in the library
s_best = idx.search(recording(stranger, 5, 5, 0, np.random.default_rng(3)))[0]
print(f'a song not in the library: best {s_best[0]} votes -> answer {"no match" if s_best[0] < MIN_SCORE else s_best[1]}')
rng = np.random.default_rng(4)
mix = recording(lib[SONG], 12, 5, None, rng) + recording(lib[64], 3, 5, None, rng)
both = idx.search(mix)[:3]
print('two songs playing at once (17 and 64):', both)
named = sum(idx.answer(c) == k for k, c in test_clips(lib))
print(f'test: {named} of 20 clips named correctly')
json.dump({'clip_hashes': len(ch), 'found': len(found), 'votes': sum(votes.values()),
           'best': [list(b) for b in best[:5]], 'rows': rows,
           'hist': sorted([[o, n] for o, n in hist.items()]), 'hist2': sorted([[o, n] for o, n in hist2.items()]),
           'runner': runner, 'ms': round(ms), 'stranger': s_best[0], 'min_score': MIN_SCORE,
           'mix': [list(b) for b in both], 'named': named},
          open('files/step6.json', 'w'), indent=1)
