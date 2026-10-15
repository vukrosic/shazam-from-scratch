"""Pictures for the film: the spectrogram of song 17 and of the noisy clip as PNG files (paper = quiet, ink = loud),
and every star of song 17 and of the clip. Writes ../public/spec/*.png and ../src/stars.json."""
import json
import os
import numpy as np
from PIL import Image
from shazam import spectrogram, peaks
from common import songs, the_clip, SONG, START_COL

ROWS = 512                    # all rows: 0 to 4,000 waves per second
PAPER, BLUE, INK = np.array([242, 236, 223]), np.array([61, 103, 136]), np.array([36, 33, 29])


def paint(spec, path):
    s = spec[:ROWS][::-1]                       # low frequencies at the bottom
    lo, hi = np.percentile(s, 50), np.percentile(s, 99.7)
    k = np.clip((s - lo) / (hi - lo), 0, 1)[..., None]
    rgb = np.where(k < .6, PAPER + (BLUE - PAPER) * (k / .6), BLUE + (INK - BLUE) * ((k - .6) / .4))
    Image.fromarray(rgb.astype(np.uint8)).save(path)
    print(path, s.shape)


lib = songs()
os.makedirs('../public/spec', exist_ok=True)
song = spectrogram(lib[SONG])
clip = spectrogram(the_clip(lib))
paint(song, '../public/spec/song17.png')
paint(clip, '../public/spec/clip17.png')
paint(spectrogram(the_clip(lib, None)), '../public/spec/clip17-clean.png')
sp, cp = peaks(song), peaks(clip)
json.dump({'rows': ROWS, 'cols': song.shape[1], 'clip_cols': clip.shape[1], 'start_col': START_COL,
           'song': sp, 'clip': cp}, open('../src/stars.json', 'w'))
print('stars', len(sp), len(cp), 'max row', max(f for _, f in sp), max(f for _, f in cp))
