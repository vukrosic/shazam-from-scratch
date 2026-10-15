"""Exercise: write the two small pieces that make the search work, then name the song.

1. pack(): put two frequency rows (0..511, 9 bits each) and a time gap (0..63, 6 bits) into one number.
   pack(96, 48, 5) should be 3148805.
2. best_song(): every clip hash that is in the table votes for (song, song slice - clip slice).
   Return the (song, difference, votes) with the most votes. For the clip below you should get song 17,
   a difference of 375 slices (12 seconds) and 49 votes.
Run: python exercise.py     The answer is in solution.py."""
from shazam import peaks, spectrogram, hashes
import shazam
from common import songs, the_clip, index


def pack(f1, f2, dt):
    # TODO: shift f1 left by 15 bits, f2 left by 6 bits, and join them with dt
    raise NotImplementedError


def best_song(clip_hashes, table):
    # TODO: count votes for every (song, difference), return the biggest as (song, difference, votes)
    raise NotImplementedError


if __name__ == '__main__':
    print('pack(96, 48, 5) =', pack(96, 48, 5), '(want 3148805)')
    shazam.pack = pack                                  # the library was built with the same packing
    lib = songs()
    idx = index(lib)
    clip_hashes = hashes(peaks(spectrogram(the_clip(lib))))
    print('best:', best_song(clip_hashes, idx.table), '(want (17, 375, 49))')
