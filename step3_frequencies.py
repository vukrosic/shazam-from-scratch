"""Step 3: turn each short slice of sound into frequency strengths, then a whole song into a spectrogram.
Results go to files/step3.json."""
import json
import time
import numpy as np
from shazam import dft, fft, spectrogram, bin_hz, slice_s, WINDOW, HOP
from common import songs, SONG, START_COL

# a tiny example: 16 samples, a wave that turns 2 times plus a half-size wave that turns 5 times
k = np.arange(16)
x = np.sin(2 * np.pi * 2 * k / 16) + 0.5 * np.sin(2 * np.pi * 5 * k / 16)
strength = np.abs(dft(x))[:9]
print('samples:', np.round(x, 2).tolist())
print('strength at 0..8 turns:', np.round(strength, 2).tolist())


def match(x, f):
    """Multiply by a test wave that turns f times, add up (sine and cosine), report the size."""
    s = np.sum(x * np.sin(2 * np.pi * f * k / 16))
    c = np.sum(x * np.cos(2 * np.pi * f * k / 16))
    return round(float(np.hypot(s, c)), 2), np.round(x * np.sin(2 * np.pi * f * k / 16), 2).tolist()


m2, prod2 = match(x, 2)
m3, prod3 = match(x, 3)
print('test wave 2 turns ->', m2, ' 3 turns ->', m3)

# the slow way and the fast way give the same answer
w = np.random.default_rng(0).normal(size=WINDOW)
diff = float(np.abs(dft(w) - fft(w)).max())
t0 = time.time(); dft(w); t_slow = time.time() - t0
t0 = time.time()
for _ in range(20): fft(w)
t_fast = (time.time() - t0) / 20
print(f'1024 samples: slow {WINDOW * WINDOW:,} multiplications {t_slow * 1000:.0f} ms, '
      f'fast {WINDOW // 2 * 10:,} multiplications {t_fast * 1000:.1f} ms, largest difference {diff:.1e}')

lib = songs()
t0 = time.time()
spec = spectrogram(lib[SONG])
t_song = time.time() - t0
print(f'spectrogram of song 17: {spec.shape} rows x slices in {t_song:.2f} s with the fast way; '
      f'the slow way would take about {t_slow * spec.shape[1]:.0f} s')
col = START_COL + 16
top = np.argsort(spec[:, col])[::-1][:3]
print(f'slice at {slice_s(col):.2f} s, loudest rows', top.tolist(), [round(bin_hz(r)) for r in top], 'Hz')
# a small copy for the picture: 6 s from 12 s, rows below 2000 Hz, 4 rows and 2 slices per cell, levels 0..9
part = spec[:256, START_COL:START_COL + 188]
cells = part.reshape(64, 4, 94, 2).max(axis=(1, 3))
lo, hi = np.percentile(cells, 5), cells.max()
levels = np.clip(np.round((cells - lo) / (hi - lo) * 9), 0, 9).astype(int)
json.dump({'x': np.round(x, 2).tolist(), 'strength': np.round(strength, 2).tolist(),
           'm2': m2, 'm3': m3, 'prod2': prod2, 'prod3': prod3, 'window': WINDOW, 'hop': HOP,
           'slice_ms': WINDOW / 8, 'hop_ms': HOP / 8, 'slow_mults': WINDOW * WINDOW, 'fast_mults': WINDOW // 2 * 10,
           't_slow_ms': round(t_slow * 1000), 't_fast_ms': round(t_fast * 1000, 1), 'diff': diff,
           't_song_fast': round(t_song, 2), 't_song_slow': round(t_slow * spec.shape[1]),
           'rows': spec.shape[0], 'slices': spec.shape[1], 'row_hz': bin_hz(1),
           'col_s': round(slice_s(col), 2), 'col_top': [round(bin_hz(r)) for r in top],
           'col_vals': np.round(spec[:256:4, col], 2).tolist(), 'image': levels.tolist()},
          open('files/step3.json', 'w'), indent=1)
