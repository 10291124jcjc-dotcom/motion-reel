"""Tiny synth + mixer for beat-locked motion-video soundtracks (numpy + scipy).

Usage (see assets/audio_template.py):

    from audio_lib import *
    mix = Mixer(dur=20, bpm=120)
    mix.add(kick(), 1.0, g=0.9)                 # place a sound at 1.0 s
    mix.sidechain([1.0, 1.5, 2.0])              # duck pads/bass that use duck=True
    mix.add(pad([48, 55, 60, 64], 2.0), 1.0, verb=0.4, duck=True)
    mix.write("soundtrack.wav")                 # reverb, glue, peak -1 dBFS

Loudness (-14 LUFS) is set later by finish.py, so don't chase overall level here.
Balance is relative: write() normalizes to the loudest peak (usually an impact), so a quiet
section stays quiet — raise its parts' gains (often 2-3x) and verify with `check.py sections`.
Everything is seeded: the same script always writes the same file.
"""
import wave
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)

# ------------------------------------------------------------------ basics
def tt(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)          # MIDI note -> Hz (60 = C4)
def noise(d): return rng.standard_normal(int(d * SR))
def saw(f, d, det=0.0): return 2 * ((tt(d) * f * (1 + det)) % 1) - 1
def filt(x, kind, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype=kind, fs=SR, output="sos"), x)
def env_ad(d, a=0.005, decay=8.0):
    t = tt(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * decay)


# ------------------------------------------------------------------ drums
def kick(big=False):
    d = 0.9 if big else 0.4; t = tt(d)
    f = 48 + 130 * np.exp(-t * (13 if big else 24))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (3 if big else 7.5))
    click = filt(noise(0.01), "highpass", 2500) * np.exp(-tt(0.01) * 300) * 0.5
    body[: len(click)] += click
    return np.tanh(body * 1.6)

def clap():
    d = 0.3; n = filt(noise(d), "bandpass", [900, 3500]); t = tt(d); e = np.zeros(len(n))
    for k, o in enumerate([0, 0.01, 0.02]): e += (t >= o) * np.exp(-(t - o).clip(0) * (60 if k < 2 else 15))
    return n * e * 0.8

def snare():
    d = 0.2; t = tt(d)
    return (filt(noise(d), "bandpass", [1500, 6000]) * 0.8 + np.sin(2 * np.pi * 190 * t) * 0.6) * np.exp(-t * 22)

def hat(open_=False):
    d = 0.16 if open_ else 0.045
    return filt(noise(d), "highpass", 7500) * np.exp(-tt(d) * (18 if open_ else 95))

def tick():  # UI tick / typing
    d = 0.02; return filt(noise(d), "bandpass", [3000, 9000]) * np.exp(-tt(d) * 260)


# ------------------------------------------------------------------ tonal
def pluck(n, d=0.3, bright=4500, decay=12):
    f = hz(n); s = saw(f, d) + 0.5 * saw(f, d, 0.004)
    return filt(s, "lowpass", bright) * np.exp(-tt(d) * decay)

def bell(n, d=1.2):
    f = hz(n); t = tt(d)
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 8))
    return s * np.exp(-t * 3.2) * np.minimum(1, t / 0.002)

def piano(n, d=1.5):  # soft felt-piano-ish tone
    f = hz(n); t = tt(d)
    s = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** (k - 1)) * np.exp(-t * (2 + k)) for k in range(1, 6))
    return filt(s, "lowpass", 3500) * np.minimum(1, t / 0.004)

def pad(notes, d, cutoff=1600, amp=0.16):
    """Stereo detuned-saw chord. notes = MIDI list."""
    s = np.zeros((int(d * SR), 2))
    for n in notes:
        for k, det in enumerate([-0.007, -0.002, 0.003, 0.008]):
            s[:, k % 2] += saw(hz(n), d, det) * 0.25
    for ch in range(2): s[:, ch] = filt(s[:, ch], "lowpass", cutoff)
    a = np.minimum(1, tt(d) / 0.06); r = np.minimum(1, (d - tt(d)) / 0.2)
    return s * (a * r)[:, None] * amp

def bass(n, d, drive=0.35):
    f = hz(n); t = tt(d)
    return (np.sin(2 * np.pi * f * t) + drive * filt(saw(f, d), "lowpass", 500)) * np.minimum(1, t / 0.005) * np.exp(-t * 4)


# ------------------------------------------------------------------ fx / UI
def blip(f0, f1, d=0.15, decay=18):  # pitched pop, Hz in / Hz out
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)

def buzz(n=40, d=0.22):  # "error" / wrong
    t = tt(d); f = hz(n)
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sign(np.sin(2 * np.pi * f * 1.5 * t)) * 0.3
    return filt(s, "lowpass", 1400) * np.exp(-t * 9)

def coin():  # "ka-ching"
    return bell(88, 0.9) * 0.6 + bell(93, 0.9) * 0.45

def whoosh(d, f0, f1, rev=False, q=0.35):
    """Band-passed noise sweeping f0 -> f1 Hz. rev=True swells into the end (pre-hit)."""
    n = noise(d); out = np.zeros_like(n); blk = 512; zi = None
    for i in range(0, len(n), blk):
        fc = f0 * (f1 / f0) ** (i / len(n))
        sos = signal.butter(2, [fc * (1 - q), min(fc * (1 + q), SR / 2 - 100)], btype="bandpass", fs=SR, output="sos")
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, n[i:i + blk], zi=zi)
    u = tt(d) / d
    return out * (np.sin(np.pi * u) ** 1.5 if not rev else u ** 3) * 2.2

def riser(d, n0, n1):
    t = tt(d); f = hz(n0) * (hz(n1) / hz(n0)) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return filt(np.sign(np.sin(ph)) * 0.3 + np.sin(ph * 2) * 0.3, "lowpass", 3500) * (t / d) ** 2.5

def impact(big=1.0):
    d = 2.2; t = tt(d)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 8)) / SR) * np.exp(-t * 1.6)
    crash = filt(noise(d), "highpass", 3000) * np.exp(-t * 2.4) * 0.35
    thud = filt(noise(d), "lowpass", 600) * np.exp(-t * 14) * 0.9
    return np.tanh((sub * 1.2 + crash + thud) * big)

def glitch(d=0.35):
    t = tt(d); n = np.round(noise(d) * 3) / 3
    return filt(n * (np.sin(2 * np.pi * 28 * t) > 0), "bandpass", [400, 6000]) * np.exp(-t * 4)


# ------------------------------------------------------------------ mixer
class Mixer:
    def __init__(self, dur, bpm=120):
        self.dur, self.bpm, self.beat = dur, bpm, 60 / bpm
        self.N = int(SR * dur)
        self.L = np.zeros(self.N); self.R = np.zeros(self.N)
        self.VL = np.zeros(self.N); self.VR = np.zeros(self.N)   # reverb send
        self.SC = np.ones(self.N)                                 # sidechain gain
        self.shift = 0.0  # add to every time — handy after cutting a section out of the picture

    def b(self, n):
        """time of beat n (float ok)"""
        return n * self.beat

    def add(self, sig, t0, g=1.0, pan=0.0, verb=0.0, duck=False):
        i = int((t0 + self.shift) * SR)
        if i >= self.N or i + len(sig) <= 0: return
        if i < 0: sig, i = sig[-i:], 0
        s = sig[: self.N - i] * g
        if s.ndim == 1: l, r = s * np.sqrt((1 - pan) / 2), s * np.sqrt((1 + pan) / 2)
        else: l, r = s[:, 0], s[:, 1]
        if duck: l = l * self.SC[i:i + len(l)]; r = r * self.SC[i:i + len(r)]
        self.L[i:i + len(l)] += l; self.R[i:i + len(r)] += r
        if verb: self.VL[i:i + len(l)] += l * verb; self.VR[i:i + len(r)] += r * verb

    def sidechain(self, times, depth=0.7):
        """Call BEFORE adding the ducked parts."""
        for kt in times:
            i = int((kt + self.shift) * SR); d = int(0.3 * SR)
            if not 0 <= i < self.N: continue
            m = min(d, self.N - i)
            self.SC[i:i + m] = np.minimum(self.SC[i:i + m], 1 - depth * np.exp(-np.arange(m) / SR * 14))

    def write(self, path, reverb=0.06, fade=0.35):
        t = tt(1.6)
        irL = filt(rng.standard_normal(len(t)) * np.exp(-t * 4.2), "lowpass", 6000)
        irR = filt(rng.standard_normal(len(t)) * np.exp(-t * 4.2), "lowpass", 6000)
        wl = signal.fftconvolve(filt(self.VL, "highpass", 250), irL)[: self.N] * reverb
        wr = signal.fftconvolve(filt(self.VR, "highpass", 250), irR)[: self.N] * reverb
        mix = np.stack([filt(self.L + wl, "highpass", 28), filt(self.R + wr, "highpass", 28)], 1)
        mix /= np.max(np.abs(mix)) + 1e-9
        mix = np.tanh(mix * 1.6) / np.tanh(1.6)          # gentle glue
        mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))     # peak -1 dBFS
        f = int(fade * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        print("wrote", path)
