"""Checks on the saved results. Run after run_all.sh."""
import json
import numpy as np
from shazam import dft, fft, pack, unpack

N = ['step1', 'step2', 'step3', 'step4', 'step5', 'step6', 'step7', 'exercise']
s1, s2, s3, s4, s5, s6, s7, ex = (json.load(open(f'files/{s}.json')) for s in N)
x = np.random.default_rng(1).normal(size=256)
assert np.abs(dft(x) - fft(x)).max() < 1e-9
assert unpack(pack(300, 7, 40)) == (300, 7, 40)
assert s1['song_samples'] == 240000 and s1['clip_samples'] == 40000
assert s2['same_noisy'] < 50 and s2['best'] == s2['right']
assert s3['strength'][2] == 8.0 and s3['strength'][5] == 4.0 and s3['m3'] == 0.0
assert s4['best_s'] == 12.0 and s4['rank'][0][0] == 17 and s4['survival'][0]['kept'] == 1.0
assert s5['by_hash'] < 1 < s5['by_row']
assert s6['best'][0][1] == 17 and s6['best'][0][2] == 375 and s6['stranger'] < s6['min_score']
assert {s6['mix'][0][1], s6['mix'][1][1]} == {17, 64} and s6['named'] == 20
assert s7['false'] == 0 and all(c['right'] == 40 for c in s7['grid'] if c['length'] >= 2 and c['snr'] is None)
assert ex['pack'] == 3148805 and ex['best'] == [17, 375, 49]
print('all tests passed')
