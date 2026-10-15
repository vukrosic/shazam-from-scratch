"""The sliding total of the compare section, at every 200th place, for the drawing. Writes ../src/curve.json."""
import json
import numpy as np
from common import songs, the_clip, SONG, START, LENGTH
from songs import RATE

lib = songs()
song, clip = lib[SONG], the_clip(lib)
n = LENGTH * RATE
places = list(range(0, len(song) - n + 1, 200))
tot = [float(np.dot(song[p:p + n], clip)) for p in places]
top = max(tot)
print(f'{len(places)} places, best at sample {places[int(np.argmax(tot))]} (12 s = {int(START * RATE)})')
json.dump({'step': 200, 'total': [round(t / top, 3) for t in tot]}, open('../src/curve.json', 'w'))
