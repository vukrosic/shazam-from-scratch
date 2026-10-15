# Shazam from scratch

Code for the video **Build Shazam From Scratch**.
A phone hears five seconds of a song in a noisy room and names it. This code builds the method from Avery Wang's 2003 paper: cut the sound into short slices, measure the strength of every frequency in each slice (a spectrogram, with our own fast Fourier transform), keep only the loudest points (the "stars"), pair each star with a few stars after it and turn each pair into one number (a hash), then let every matching hash vote for a song and a time difference.
The paper: Avery Li-Chun Wang, "An Industrial-Strength Audio Search Algorithm", ISMIR 2003.

```bash
pip install numpy
sh run_all.sh         # every step, the solution and the checks; expected output is in demo-output.txt
```

Nothing is downloaded and nothing is trained. The 100 songs in the library are made by `songs.py` (sine-wave instruments and drums, fixed seeds), and the room noise is made by the same code. `run_all.sh` takes about a minute on a laptop CPU.

```python
hash  = (row of star 1) << 15 | (row of star 2) << 6 | (slices between them)
votes[(song, song slice - clip slice)] += 1      # the right song gets a tall spike at one difference
```

## Results

The clip: song 17, from 12 s, 5 s long, at 30 % volume, with room noise as loud as the music.

| Method | Finds song 17? | Time for one question, 100 songs |
| --- | --- | --- |
| equal samples | 3 of 40,000 samples equal | — |
| slide the clip's samples over every song | yes | about 0.5 min (7 days for 1.8 million songs) |
| slide the clip's stars over every song's stars | yes, 24 stars line up | 0.5 s (about 2 hours for 1.8 million songs) |
| look up pair hashes, count votes | yes, 49 votes at 12.00 s; next song 2 | about 15 ms |

Full test, 40 clips per cell, right answers (the rest are mostly "no match"; a song needs 12 lined-up votes):

| Clip length | no noise | noise = music (0 dB) | −3 dB | −6 dB | −9 dB (noise 2.8× as loud) |
| --- | --- | --- | --- | --- | --- |
| 1 s | 36 | 9 | 3 | 3 | 0 |
| 2 s | 40 | 29 | 28 | 12 | 4 |
| 3 s | 40 | 36 | 36 | 24 | 5 |
| 5 s | 40 | 39 | 38 | 28 | 8 (3 wrong) |
| 10 s | 40 | 40 | 40 | 37 (1 wrong) | 25 |

100 songs that are not in the library: 0 wrongly named. Times change from machine to machine.

## Files

| File | What it does |
| --- | --- |
| `songs.py` | makes the songs, the room noise and the phone recording |
| `shazam.py` | spectrogram (slow DFT and fast FFT), peaks, hashes, the index and the vote |
| `step1_samples.py` … `step7_test.py` | one step of the video each |
| `exercise.py` | write `pack()` and the vote yourself; `solution.py` has the answer |
| `tests.py` | checks the saved results |

## Words

| In the video | Usual name | In the code |
| --- | --- | --- |
| slice | frame / window (1024 samples, a new one every 256) | `WINDOW`, `HOP` |
| row | frequency bin (7.8 Hz each) | `bin_hz` |
| star | spectrogram peak | `peaks` |
| star map | constellation map | list of `(slice, row)` |
| pair number | hash / fingerprint | `pack`, `hashes` |
| zone | target zone | `ZONE_END`, `ZONE_FREQ` |
| vote | offset histogram bin | `Index.votes` |

MIT license.
