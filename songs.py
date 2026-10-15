"""Songs made by our own code, so nothing is downloaded and no music is licensed.

Every song has its own speed, key, instrument sound, melody, bass line and drums.
The seed fixes everything, so song 17 is the same song on every computer."""
import wave
import numpy as np

RATE = 8000          # samples per second, the rate in Wang's 2003 paper
SECONDS = 30         # length of every song in the library
MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]


def hz(midi, a4=440.0):
    return a4 * 2 ** ((midi - 69) / 12)


def tone(freq, length, harm, decay, wobble=0.0, rate=RATE):
    """One note: a sine wave plus a few harmonics, a fast start and a slow fade.
    wobble makes the pitch sway a little, five times a second, like a singer's voice."""
    t = np.arange(int(length * rate)) / rate
    phase = 2 * np.pi * freq * (t - wobble / (2 * np.pi * 5) * np.cos(2 * np.pi * 5 * t))
    out = np.zeros_like(t)
    for k, a in enumerate(harm, start=1):
        if freq * k < rate / 2:
            out += a * np.sin(k * phase)
    env = np.minimum(t / 0.005, 1) * np.exp(-t / decay)
    return out * env


def drum(kind, kit, rng, rate=RATE):
    """kit holds this song's own drum sounds: kick pitch, snare colour, hat length."""
    t = np.arange(int(0.18 * rate)) / rate
    if kind == 'kick':                       # a low tone that drops in pitch
        f = kit['kick_hz'] * np.exp(-t / 0.04) + kit['kick_hz'] * 0.4
        return np.sin(2 * np.pi * np.cumsum(f) / rate) * np.exp(-t / 0.08)
    noise = rng.uniform(-1, 1, len(t))
    if kind == 'snare':
        body = np.sin(2 * np.pi * kit['snare_hz'] * t)
        return (noise * 0.6 + body * 0.5) * np.exp(-t / 0.05) * 0.6
    hat = noise - np.concatenate([[0], noise[:-1]])   # keep the high part of the noise
    return hat * np.exp(-t / kit['hat_s']) * 0.25


def make_song(seed, seconds=SECONDS, rate=RATE):
    rng = np.random.default_rng(seed)
    bpm = int(rng.integers(72, 160))
    beat = 60 / bpm
    root = int(rng.integers(45, 57))
    scale = MAJOR if rng.random() < 0.5 else MINOR
    harm = rng.uniform(0.1, 1, 5) ** 2
    harm = np.concatenate([[1.0], harm])
    decay = float(rng.uniform(0.12, 0.5))
    a4 = float(rng.uniform(425, 455))            # every band tunes a little differently
    wobble = float(rng.uniform(0.0, 0.02))
    kit = {'kick_hz': float(rng.uniform(70, 160)), 'snare_hz': float(rng.uniform(150, 400)),
           'hat_s': float(rng.uniform(0.008, 0.03))}
    hats = int(rng.choice([1, 2, 4]))         # hi-hat every half beat, every beat or every two beats
    out = np.zeros(int(seconds * rate) + rate)

    def put(sound, at):
        i = int(at * rate)
        n = min(len(sound), len(out) - i)
        if n > 0:
            out[i:i + n] += sound[:n]

    # two melody phrases of two bars, played in the order A A B A, then again
    def phrase():
        deg, notes = int(rng.integers(0, 7)), []
        for _ in range(16):
            deg = int(np.clip(deg + rng.integers(-2, 3), 0, 13))
            notes.append(None if rng.random() < 0.15 else deg)
        return notes
    a, b = phrase(), phrase()
    chords = [int(c) for c in rng.choice([0, 3, 4, 5], 4)]
    melody = (a + a + b + a) * 8
    t, i = 0.0, 0
    while t < seconds:
        d = melody[i % len(melody)]
        if d is not None:
            midi = root + 12 + 12 * (d // 7) + scale[d % 7]
            put(0.35 * tone(hz(midi, a4), beat * 0.5 + decay, harm, decay, wobble), t)
        if i % 8 == 0:                                       # a bass note every bar
            c = chords[(i // 8) % 4]
            put(0.45 * tone(hz(root - 12 + scale[c], a4), beat * 4, [1, 0.5, 0.2], 0.6), t)
        beat_no = i // 2
        if i % 2 == 0:
            put(0.6 * drum('kick' if beat_no % 2 == 0 else 'snare', kit, rng), t)
        if i % hats == 0:
            put(drum('hat', kit, rng), t)
        t += beat / 2
        i += 1
    out = out[:int(seconds * rate)]
    return out / np.abs(out).max() * 0.9, {'seed': seed, 'bpm': bpm, 'root': root,
                                           'scale': 'major' if scale is MAJOR else 'minor'}


def library(n, first_seed=1):
    """Songs 1..n. Song k has seed k."""
    return {k: make_song(k)[0] for k in range(first_seed, first_seed + n)}


def save_wav(path, samples, rate=RATE):
    data = (np.clip(samples, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def room_noise(n, rng, rate=RATE):
    """A noisy room made by our code: hiss plus a song that is not in the library, mixed together."""
    hiss = rng.normal(0, 1, n)
    other, _ = make_song(9000 + int(rng.integers(0, 1000)), seconds=n / rate + 1)
    start = int(rng.integers(0, rate))
    chatter = other[start:start + n]
    noise = hiss / hiss.std() + chatter / chatter.std()
    return noise / noise.std()


def recording(song, start_s, length_s, snr_db, rng, volume=0.3, rate=RATE):
    """What a phone hears: a piece of the song, quieter, with room noise at the given signal-to-noise ratio."""
    i = int(start_s * rate)
    clip = song[i:i + int(length_s * rate)] * volume
    if snr_db is None:
        return clip
    noise = room_noise(len(clip), rng)
    noise *= clip.std() / 10 ** (snr_db / 20)
    return clip + noise
