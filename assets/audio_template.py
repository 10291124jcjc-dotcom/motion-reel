"""Soundtrack for index.html — every cue sits on the same timeline as the picture.

Workflow: list the visual events (slams, transitions, impacts, UI pops) with their times from
index.html, then give each one a sound here. Sections follow the story: tension → turn → drop → resolve.
Run:  python audio.py   ->  soundtrack.wav   (finish.py normalizes to -14 LUFS)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "tools"))
from audio_lib import *

DUR, BPM = 6.0, 120
mix = Mixer(DUR, BPM)
B = mix.beat  # 0.5 s at 120 BPM

# ---- harmony: one chord per bar (2 s at 120 BPM). MIDI: 36=C2, 48=C3, 60=C4
CHORDS = [(0.0, [48, 55, 60, 64], 36),   # C
          (2.0, [43, 50, 55, 59], 31),   # G
          (4.0, [45, 52, 57, 60], 33)]   # Am → resolves on the logo

# ---- groove: kicks on the beat from the first slam, ducking pad & bass
kicks = [i * B for i in range(int(DUR / B))]
mix.sidechain(kicks)
for kt in kicks: mix.add(kick(), kt, 0.9)
for i, kt in enumerate(kicks):
    if i % 2: mix.add(clap(), kt, 0.45, verb=0.3)
    mix.add(hat(i % 4 == 3), kt + B / 2, 0.22, pan=0.3)
for t0, notes, root in CHORDS:
    mix.add(pad(notes + [notes[1] + 12], 2.0, 2200), t0, 1.0, verb=0.4, duck=True)
    for k in range(8): mix.add(bass(root + (12 if k % 2 else 0), 0.24), t0 + k * B / 2, 0.4, duck=True)

# ---- hits locked to picture events (times copied from index.html)
mix.add(impact(0.8), 0.1, 0.6)                           # 'MOTION' slam
mix.add(impact(1.0), 0.5, 0.7)                           # '动态设计' slam
for k in range(8): mix.add(tick(), 1.0 + k * 0.035, 0.25)   # subline typing
mix.add(whoosh(0.45, 300, 8000), 1.78, 0.45)             # iris transition @2.0
for k in range(6): mix.add(blip(hz(76 + 2 * k), hz(72 + 2 * k), 0.15), 2.05 + k * 0.08, 0.12, verb=0.4)  # grid pops
mix.add(whoosh(0.4, 6000, 300), 3.8, 0.4)                # push @4.0
mix.add(kick(True), 4.05, 0.9); mix.add(impact(1.2), 4.05, 0.9, verb=0.3)   # logo lands
for k, n in enumerate([84, 88, 91, 96]): mix.add(bell(n), 4.3 + k * 0.07, 0.1, verb=0.7)
mix.add(blip(900, 1400, 0.25, 12), 4.7, 0.3)             # CTA pop

mix.write("soundtrack.wav")
