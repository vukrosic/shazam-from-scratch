"""Solution to exercise.py. Results go to files/exercise.json."""
import json
from collections import Counter
from shazam import peaks, spectrogram, hashes
from common import songs, the_clip, index


def pack(f1, f2, dt):
    return (f1 << 15) | (f2 << 6) | dt


def best_song(clip_hashes, table):
    votes = Counter()
    for h, t in clip_hashes:
        for song, ts in table.get(h, ()):
            votes[(song, ts - t)] += 1
    (song, diff), n = votes.most_common(1)[0]
    return song, diff, n


if __name__ == '__main__':
    lib = songs()
    idx = index(lib)
    clip_hashes = hashes(peaks(spectrogram(the_clip(lib))))
    p = pack(96, 48, 5)
    b = best_song(clip_hashes, idx.table)
    print('pack(96, 48, 5) =', p)
    print('best:', b)
    json.dump({'pack': p, 'best': list(b)}, open('files/exercise.json', 'w'), indent=1)
