"""Step 1: sound is a list of numbers. Results go to files/step1.json."""
import json
import numpy as np
from songs import RATE, make_song, save_wav
from common import songs, the_clip, SONG, START

t = np.arange(10) / RATE
beep = np.sin(2 * np.pi * 440 * t)                  # the note A: 440 waves per second
print('440 Hz, first 10 samples:', np.round(beep, 3).tolist())
lib = songs()
song = lib[SONG]
_, info = make_song(SONG)
i = int(START * RATE)
clip = the_clip(lib)
print(f'song {SONG}: {len(song):,} samples, {info}')
print('song at 12 s:', np.round(song[i:i + 8], 3).tolist())
print('phone clip  :', np.round(clip[:8], 3).tolist())
save_wav('files/song17.wav', song)
save_wav('files/clip17.wav', clip / np.abs(clip).max() * 0.9)
save_wav('files/song64.wav', lib[64])
json.dump({'rate': RATE, 'beep': np.round(beep, 3).tolist(), 'song_samples': len(song), 'info': info,
           'song_at': np.round(song[i:i + 8], 3).tolist(), 'clip_at': np.round(clip[:8], 3).tolist(),
           'clip_samples': len(clip), 'wave': np.round(song[i:i + 400:4], 3).tolist(),
           'clip_wave': np.round(clip[:400:4], 3).tolist()},
          open('files/step1.json', 'w'), indent=1)
