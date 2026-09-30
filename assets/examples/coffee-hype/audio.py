"""Soundtrack for 山野咖啡开业 (20 s, 120 BPM) — every cue sits on the picture's timeline.

Sections: hook (Am, punchy) -> build (F-G, snare roll, riser) -> DROP on the offer at 4.0 (C major groove)
-> origin/roast (groove + pentatonic plucks, riser) -> vortex gap 12.0 -> montage (snare per cut)
-> place -> resolve on C at the logo 17.0.
Run:  python audio.py   ->  soundtrack.wav   (finish.py normalizes to -14 LUFS)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "tools"))
from audio_lib import *

DUR, BPM = 20.0, 120
mix = Mixer(DUR, BPM)
B = mix.beat  # 0.5 s

CH = {  # pad notes, bass root
    'Am': ([57, 60, 64, 69], 45), 'F': ([53, 57, 60, 65], 41), 'G': ([55, 59, 62, 67], 43), 'C': ([55, 60, 64, 67], 36),
}
PROG = [(0, 'Am'), (2, 'F'), (3, 'G'), (4, 'C'), (6, 'G'), (8, 'Am'), (10, 'F'), (11, 'G'), (12.0, None),
        (12.5, 'C'), (13.5, 'G'), (14.5, 'Am'), (15.5, 'F'), (16.5, 'G'), (17, 'C'), (DUR, None)]


def rng_(a, b, step=B):
    out, x = [], a
    while x < b - 1e-6: out.append(round(x, 3)); x += step
    return out


# ---- groove
kicks = rng_(0, 3.0) + rng_(4.0, 12.0) + rng_(12.5, 17.0) + rng_(17.5, 20.0)
mix.sidechain(kicks + [17.0])
for kt in kicks:
    mix.add(kick(), kt, 0.85 if 17.5 <= kt else 0.95)
claps = [t for t in rng_(4.5, 12.0, 1.0) + rng_(13.5, 17.0, 1.0)]
for ct in claps: mix.add(clap(), ct, 0.5, verb=0.3)
for ht in rng_(0.25, 2.0) + rng_(4.25, 12.0) + rng_(14.75, 17.0) + rng_(17.75, 19.8):
    mix.add(hat(), ht, 0.28, pan=0.3)
for ht in rng_(2.0, 4.0, B / 2) + rng_(12.5, 13.5, B / 2):              # 16ths in the build and montage
    mix.add(hat(), ht, 0.2, pan=-0.3)
for k, st in enumerate(rng_(3.0, 4.0, B / 4)):                            # snare roll into the drop
    mix.add(snare(), st, 0.18 + 0.05 * k, verb=0.2)

# ---- harmony: pads + 8th-note bass, ducked by the kick
for (t0, name), (t1, _) in zip(PROG, PROG[1:]):
    if not name: continue
    notes, root = CH[name]; d = t1 - t0
    big = t0 >= 4.0
    mix.add(pad(notes + [notes[1] + 12], d, 2600 if big else 1500, amp=0.2 if big else 0.24), t0, 1.0, verb=0.4, duck=True)
    for k, bt in enumerate(rng_(t0, t1, B / 2)):
        mix.add(bass(root + (12 if k % 2 and big else 0), 0.24), bt, 0.55 if big else 0.7, duck=True)

# ---- melody: C-major pentatonic plucks over the drop / origin (8ths)
MOTIF = [72, 76, 79, 76, 81, 79, 76, 74]
for bar in range(4, 12, 2):
    for k, n in enumerate(MOTIF):
        if bar >= 10 and k % 2: continue                                   # thin out under the roast
        mix.add(pluck(n if bar != 8 else n - 3, 0.28), bar + k * B / 2, 0.22, pan=0.25 * (1 if k % 2 else -1), verb=0.35)
for k, n in enumerate([72, 74, 76, 79, 81, 84, 86, 88]):                   # route line drawing 8.2-9.25
    mix.add(pluck(n, 0.25, 6000), 8.2 + k * 0.13, 0.2, verb=0.4)
for bar in (12.5, 14.5, 15.5):
    for k, n in enumerate(MOTIF[:4]):
        mix.add(pluck(n, 0.25), bar + k * B / 2, 0.18, verb=0.3)

# ---- hits locked to picture events (times from index.html)
mix.add(impact(1.0), 0.02, 0.8); mix.add(glitch(0.3), 0.02, 0.35)        # 早八人 glitch slam
mix.add(whoosh(0.2, 5000, 400), 0.36, 0.35); mix.add(impact(0.8), 0.52, 0.6)  # 打工人 smear
mix.add(impact(1.2), 1.02, 0.85); mix.add(kick(True), 1.02, 0.8)          # 续命了吗？ punch
for k in range(5): mix.add(blip(hz(76 + k), hz(72 + k), 0.12), 1.02 + k * 0.035, 0.12)  # bounce letters
mix.add(whoosh(0.45, 300, 7000), 1.78, 0.55)                             # tear 2.0
for k in range(7): mix.add(tick(), 1.87 + k * 0.035, 0.22)               # 小寨新开了一家
mix.add(whoosh(0.35, 6000, 800), 2.2, 0.4); mix.add(impact(0.9), 2.35, 0.6, verb=0.3)  # 山野咖啡 smear
for k in range(12): mix.add(tick(), 2.75 + k * 0.045, 0.18, pan=0.2)      # scramble
mix.add(riser(1.25, 55, 79), 2.75, 0.3)                                  # riser into the drop
mix.add(whoosh(0.3, 400, 9000, rev=True), 3.72, 0.5)                     # zoom 4.0
mix.add(kick(True), 4.0, 1.0); mix.add(impact(1.4), 4.0, 1.0, verb=0.3)  # THE DROP
mix.add(blip(700, 1200, 0.18), 4.25, 0.3)                                # ticket pop
mix.add(impact(0.9), 4.38, 0.55)                                         # 半价 slam
mix.add(snare(), 6.0, 0.35)                                              # cut 6.0
mix.add(blip(600, 900, 0.16), 5.88, 0.35); mix.add(blip(800, 1200, 0.16), 6.18, 0.35)  # cups pop
for k in range(10): mix.add(tick(), 6.4 + k * 0.03, 0.18)                # dates draw
mix.add(impact(1.0), 6.92, 0.7); mix.add(coin(), 6.95, 0.35, verb=0.5)   # stamp 半价
mix.add(glitch(0.4), 7.82, 0.4); mix.add(whoosh(0.35, 2000, 9000), 7.85, 0.3)  # slice 8.0
mix.add(blip(500, 800, 0.2), 7.92, 0.3)                                  # 保山 pin
mix.add(blip(900, 1500, 0.2), 9.22, 0.35); mix.add(impact(0.7), 9.3, 0.45)  # 西安 pin
mix.add(whoosh(0.45, 500, 6000), 9.77, 0.45)                             # iris 10.0
for bt in (10.0, 10.5, 11.0, 11.5): mix.add(impact(0.55), bt, 0.3)       # field shockwaves
for k in range(12): mix.add(tick(), 10.4 + k * 0.045, 0.15, pan=-0.2)    # ROASTED IN STORE
mix.add(riser(1.4, 50, 86), 11.0, 0.32)
mix.add(whoosh(0.5, 8000, 200, rev=True), 12.0, 1.0)                     # vortex collapse
mix.add(riser(0.5, 74, 98), 12.0, 0.45)                                  # keep the breath alive (was a dead patch)
for k in range(8): mix.add(snare(), 12.0 + k * B / 4, 0.12 + 0.04 * k)    # 32nd roll into the montage
for ct in (12.5, 12.75, 13.0, 13.25):                                    # montage cuts
    mix.add(snare(), ct, 0.4, verb=0.2); mix.add(tick(), ct, 0.4); mix.add(glitch(0.12), ct, 0.15)
mix.add(impact(1.1), 13.5, 0.8); mix.add(kick(True), 13.5, 0.8)          # 都来一杯
for k in range(4): mix.add(blip(hz(79 + 2 * k), hz(84 + 2 * k), 0.14), 13.57 + k * 0.08, 0.25, verb=0.3)  # cups row
mix.add(whoosh(0.5, 300, 8000), 14.25, 0.5)                              # stripes 14.5
mix.add(blip(1500, 400, 0.28, 8), 14.72, 0.3); mix.add(impact(0.8), 14.98, 0.6)  # pin drop
for k in range(12): mix.add(tick(), 15.1 + k * 0.04, 0.2)                # 88 counter
mix.add(coin(), 15.6, 0.25, verb=0.4)
for k in range(5): mix.add(blip(hz(79 + k), hz(83 + k), 0.12), 15.7 + k * 0.035, 0.14)  # 顺路来一杯
mix.add(whoosh(0.45, 6000, 300, rev=True), 16.55, 0.5)                   # collapse
mix.add(kick(True), 17.02, 1.0); mix.add(impact(1.5), 17.02, 1.0, verb=0.4)  # logo lands
for k, n in enumerate([84, 88, 91, 96]): mix.add(bell(n), 17.25 + k * 0.07, 0.14, verb=0.7)
mix.add(blip(900, 1400, 0.25, 12), 17.85, 0.35)                          # CTA pop
for k in range(8): mix.add(tick(), 18.15 + k * 0.03, 0.15)               # address
mix.add(bell(96, 1.5), 18.3, 0.12, verb=0.6); mix.add(bell(91, 1.5), 19.3, 0.12, verb=0.6)  # sheens
mix.add(pad([48, 55, 60, 64, 67, 72], 3.0, 3200, amp=0.22), 17.0, 1.0, verb=0.5)  # resolve

mix.write("soundtrack.wav")
