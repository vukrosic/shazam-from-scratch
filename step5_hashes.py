"""Step 5: pair each star with a few stars just after it and turn every pair into one number (a hash).
Build the library's table: hash -> where it appears. Results go to files/step5.json."""
import json
from collections import Counter
import numpy as np
from shazam import spectrogram, peaks, hashes, pack, bin_hz, slice_s, FAN_OUT, ZONE_END, ZONE_FREQ
from common import songs, the_clip, index, SONG, START_COL

lib = songs()
idx = index(lib)
clip = the_clip(lib)
cpk = peaks(spectrogram(clip))
song_stars = {(t - START_COL, f) for t, f in peaks(spectrogram(lib[SONG]))}
# the worked example: the first clip star that is also a song star and has a full set of partners
for a, (t1, f1) in enumerate(cpk):
    zone = [(t2, f2) for t2, f2 in cpk[a + 1:] if 1 <= t2 - t1 <= ZONE_END and abs(f2 - f1) <= ZONE_FREQ]
    if (t1, f1) in song_stars and len(zone) >= FAN_OUT:
        break
pairs = zone[:FAN_OUT]
example = [{'t2': t2, 'f2': f2, 'dt': t2 - t1, 'hash': pack(f1, f2, t2 - t1), 'f2_hz': round(bin_hz(f2)),
            'in_song': (t2, f2) in song_stars} for t2, f2 in pairs]
print(f'anchor star: slice {t1} ({slice_s(t1):.2f} s), row {f1} ({bin_hz(f1):.0f} Hz)')
for e in example[:3]:
    print(f"  partner row {e['f2']} ({bin_hz(e['f2']):.0f} Hz), {e['dt']} slices later -> hash {e['hash']:,}")

# how many places in the library does one lookup return?
rows = Counter()
for k, s in lib.items():
    rows.update(f for _, f in peaks(spectrogram(s)))
by_row = float(np.mean([rows[f] for _, f in cpk]))
ch = hashes(cpk)
by_hash = float(np.mean([len(idx.table.get(h, ())) for h, _ in ch]))
print(f'look up one star by its row: {by_row:.0f} places in the library on average')
print(f'look up one pair by its hash: {by_hash:.2f} places on average')
print(f'clip: {len(cpk)} stars -> {len(ch)} hashes')
print(f'library: {idx.songs} songs, {idx.entries:,} entries ({idx.entries // idx.songs:,} per song), '
      f'{len(idx.table):,} different hashes, {idx.entries * 8 / 1e6:.1f} MB at 8 bytes per entry')

# do the pairs survive the noise? (both stars must survive)
song_h = hashes(peaks(spectrogram(lib[SONG])))
song_span = {(h, t - START_COL) for h, t in song_h if START_COL <= t < START_COL + 150}
kept = len(song_span & {(h, t) for h, t in ch}) / len(song_span)
print(f'pairs of the song that are still in the noisy clip: {kept:.0%}')
json.dump({'anchor': [t1, f1], 'anchor_hz': round(bin_hz(f1)), 'anchor_s': round(slice_s(t1), 2), 'zone_end': ZONE_END,
           'zone_freq': ZONE_FREQ, 'fan_out': FAN_OUT, 'example': example, 'by_row': round(by_row), 'by_hash': round(by_hash, 2),
           'clip_stars': len(cpk), 'clip_hashes': len(ch), 'entries': idx.entries, 'per_song': idx.entries // idx.songs,
           'distinct': len(idx.table), 'mb': round(idx.entries * 8 / 1e6, 1), 'pair_kept': round(kept, 3),
           'possible': 512 * 512 * 64},
          open('files/step5.json', 'w'), indent=1)
