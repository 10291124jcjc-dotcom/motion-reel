"""Soundtrack for Claude_Showreel (15 s, 128 BPM, 32 beats) — every cue sits on the picture's timeline.

Sections: hook (Am, a bouncing ball you can hear) -> identity (F-G, snare roll + riser)
-> DROP at b8 3.75 s (C-G-Am-F groove, pluck motif) -> 2nd drop b16 7.5 s (tunnel, brighter)
-> field (half-time impacts on the beat shockwaves) -> vortex breath -> proof (F-G, ticks per counter)
-> resolve on C when the ball lands as the logo at b26 12.19 s.
Run:  python audio.py   ->  soundtrack.wav   (finish.py normalizes to -14 LUFS)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "tools"))
from audio_lib import *

DUR, BPM = 15.0, 128
mix = Mixer(DUR, BPM)
B = mix.beat           # 0.46875 s
b = mix.b              # b(n) = time of beat n

CH = {  # pad notes, bass root
    'Am': ([57, 60, 64, 69], 45), 'F': ([53, 57, 60, 65], 41), 'G': ([55, 59, 62, 67], 43), 'C': ([55, 60, 64, 67], 36),
}
PROG = [(0, 'Am'), (4, 'F'), (6, 'G'), (8, 'C'), (10, 'G'), (12, 'Am'), (14, 'F'), (16, 'C'), (18, 'G'),
        (20, 'Am'), (22, 'G'), (22.6, None), (23, 'F'), (24.5, 'G'), (26, 'C'), (32, None)]


def beats(a, c, step=1.0):
    out, x = [], a
    while x < c - 1e-6: out.append(round(b(x), 4)); x += step
    return out


# ---- groove
kicks = beats(0, 4) + beats(4, 8) + beats(8, 20) + beats(20, 23) + beats(23, 26) + beats(27, 31)
mix.sidechain(kicks + [b(26)])
for kt in kicks: mix.add(kick(), kt, 0.9)
for ct in beats(5, 8, 2) + beats(9, 20, 2) + beats(24, 26, 1) + beats(27, 31, 2): mix.add(clap(), ct, 0.5, verb=0.3)
for ht in beats(0.5, 4) + beats(8.5, 20) + beats(26.5, 31):              # off-beat hats
    mix.add(hat(), ht, 0.3, pan=0.3)
for ht in beats(6, 8, .25) + beats(12, 16, .25) + beats(23, 26, .25):      # 16ths in the build, morph/rhythm, proof
    mix.add(hat(), ht, 0.18, pan=-0.3)
for k, st in enumerate(beats(7, 8, .25) + beats(7.5, 8, .125)):           # snare roll into the drop
    mix.add(snare(), st, 0.15 + 0.03 * k, verb=0.2)

# ---- harmony: pads + 8th-note bass, ducked by the kick
for (t0, name), (t1, _) in zip(PROG, PROG[1:]):
    if not name: continue
    notes, root = CH[name]; d = b(t1) - b(t0)
    big = t0 >= 8
    mix.add(pad(notes + [notes[1] + 12], d, 2800 if t0 >= 16 else 2200 if big else 1400, amp=0.2 if big else 0.26),
            b(t0), 1.0, verb=0.4, duck=True)
    for k, bt in enumerate(beats(t0, t1, .5)):
        mix.add(bass(root + (12 if k % 2 and big else 0), 0.22), bt, 0.55 if big else 0.75, duck=True)

# ---- melody: C-major pentatonic plucks over the drops (8ths)
MOTIF = [72, 76, 79, 76, 81, 79, 76, 74]
for bar, lift in ((8, 0), (12, -3), (16, 12), (18, 7)):
    for k, n in enumerate(MOTIF):
        mix.add(pluck(n + lift, 0.26), b(bar + k * .5), 0.2, pan=0.25 * (1 if k % 2 else -1), verb=0.35)
for k, n in enumerate([72, 76, 79, 84]):
    mix.add(pluck(n, 0.3, 6000), b(26.5 + k * .5), 0.2, verb=0.5)

# ---- hits locked to picture events (times from index.html)
# hook: a ball you can hear
mix.add(impact(0.9), 0.0, 0.7); mix.add(glitch(0.3), 0.0, 0.45)          # 别眨眼 glitch
mix.add(whoosh(0.45, 2500, 500), 0.02, 0.25)                              # the fall
for k, lt in enumerate([b(1), b(2), b(3)]):                                # landings: boing + thud
    mix.add(blip(hz(55 + 5 * k), hz(67 + 5 * k), 0.22, 10), lt, 0.5)
    mix.add(kick(True), lt, 0.7)
mix.add(glitch(0.2), b(1), 0.3)                                          # re-glitch on landing 1
mix.add(impact(0.8), b(2), 0.55)                                          # cut to orange
for k in range(10): mix.add(tick(), b(2) + k * 0.03, 0.3)               # 15 counter
mix.add(whoosh(0.25, 6000, 900), b(2) - 0.1, 0.3)                        # 秒 smear
mix.add(impact(1.3), b(3), 0.85)                                          # 看好了 punch
for k in range(3): mix.add(blip(hz(79 + 3 * k), hz(74 + 3 * k), 0.12), b(3) + .05 + k * 0.04, 0.18)
mix.add(whoosh(0.4, 300, 3000, rev=True), b(3) + .1, 0.35)                 # ball melts into the line
mix.add(whoosh(0.45, 300, 7000), b(4) - 0.22, 0.55)                       # tear
# identity
for k in range(5): mix.add(tick(), b(4) - .15 + k * 0.03, 0.25)          # 你好，我是
mix.add(whoosh(0.35, 6000, 800), b(4) - .12, 0.4); mix.add(impact(0.8), b(4), 0.5, verb=0.3)  # CLAUDE smear
mix.add(whoosh(0.3, 800, 3000, rev=True), b(5) - .3, 0.3)                  # full stop falls
mix.add(blip(1400, 700, 0.2, 14), b(5), 0.45); mix.add(bell(84, 0.8), b(5), 0.12, verb=0.5)  # ... lands
for k in range(5): mix.add(tick(), b(5) + .05 + k * 0.05, 0.22)         # 动态设计师
for k in range(10): mix.add(tick(), b(5) + .3 + k * 0.025, 0.16, pan=0.2)  # stroke line
for k in range(12): mix.add(tick(), b(5) + .5 + k * 0.04, 0.14, pan=-0.2) # scramble
mix.add(riser(1.0, 52, 84), b(6), 0.3)
mix.add(whoosh(0.35, 400, 9000, rev=True), b(8) - 0.35, 0.55)             # zoom
# DROP: 弹性
mix.add(kick(True), b(8), 1.0); mix.add(impact(1.4), b(8), 0.95, verb=0.3)
for i in range(5):
    mix.add(blip(hz(67 + 2 * i), hz(79 + 2 * i), 0.2, 9), b(8) - .1 + i * .05, 0.2, pan=(i - 2) * .3)   # springs settle
    mix.add(blip(hz(74 + 2 * i), hz(62 + 2 * i), 0.2, 9), b(9) + i * .04, 0.22, pan=(i - 2) * .3)      # tug
# 缓动
mix.add(snare(), b(10), 0.35, verb=0.2)
mix.add(whoosh(0.7, 400, 5000), b(10) + .2, 0.35)                          # dot rides the curve
mix.add(blip(900, 1300, 0.15), b(11) + .1, 0.22)                           # overshoot
# 形变
mix.add(glitch(0.3), b(12) - .18, 0.4); mix.add(whoosh(0.3, 2000, 9000), b(12) - .18, 0.3)  # slice
for k, s in enumerate([b(12), b(12.5), b(13), b(13.5)]): mix.add(blip(hz(72 + 3 * k), hz(84 + 3 * k), 0.14), s, 0.28, verb=0.3)
# 节奏: 8th cuts
for ct in (b(14), b(14.5), b(15), b(15.5)):
    mix.add(snare(), ct, 0.4, verb=0.2); mix.add(tick(), ct, 0.4); mix.add(glitch(0.1), ct, 0.15)
mix.add(whoosh(0.4, 500, 6000), b(16) - .22, 0.45)                          # iris
# 2nd drop: tunnel + ring
mix.add(kick(True), b(16), 1.0); mix.add(impact(1.3), b(16), 0.9, verb=0.35)
for bt in (b(17), b(18), b(19)):
    mix.add(whoosh(0.35, 7000, 400), bt - .05, 0.3); mix.add(impact(0.5), bt, 0.3)
for k in range(12): mix.add(tick(), b(16) + .15 + k * 0.04, 0.14)        # DEPTH scramble
mix.add(whoosh(0.4, 6000, 300), b(20) - .2, 0.4)                            # bars
# 系统: field shockwaves, vortex, dot
for bt in (b(20), b(21), b(22)): mix.add(impact(0.7), bt, 0.45, verb=0.3)
for k in range(10): mix.add(tick(), b(20) + .15 + k * 0.045, 0.15, pan=0.2)
mix.add(whoosh(0.7, 8000, 200, rev=True), b(22), 0.8)                       # vortex collapse
mix.add(riser(0.45, 74, 98), b(22) + .02, 0.35)                             # keep the breath alive
mix.add(blip(500, 1100, 0.2), b(22) + .35, 0.35)                            # dot appears
# proof
mix.add(kick(True), b(23), 0.9); mix.add(impact(1.0), b(23), 0.7)          # disc fills the frame
for i, bt in enumerate((b(23) + .1, b(24) - .02, b(25) - .02)):
    for k in range(10): mix.add(tick(), bt + k * 0.035, 0.28)                # counters race
    mix.add(blip(hz(76 + 4 * i), hz(88 + 4 * i), 0.14), bt + .36, 0.3)
mix.add(coin(), b(25) + .4, 0.3, verb=0.4)
for k in range(10): mix.add(tick(), b(25) + .08 + k * 0.04, 0.12)         # render(t) scramble
mix.add(whoosh(0.3, 600, 4000, rev=True), b(26) - .3, 0.45)                 # ball falls
# end card
mix.add(kick(True), b(26), 1.0); mix.add(impact(1.5), b(26), 1.0, verb=0.4)
for k, n in enumerate([84, 88, 91, 96]): mix.add(bell(n), b(26) + .1 + k * 0.07, 0.13, verb=0.7)
for k in range(6): mix.add(blip(hz(76 + k), hz(81 + k), 0.1), b(26) + .08 + k * 0.05, 0.12)  # Claude spin
for k in range(8): mix.add(tick(), b(26) + .3 + k * 0.03, 0.14)
mix.add(blip(900, 1400, 0.25, 12), b(27) + .1, 0.35)                        # CTA pop
mix.add(bell(96, 1.5), b(28), 0.12, verb=0.6); mix.add(bell(91, 1.5), b(30), 0.12, verb=0.6)  # sheens
mix.add(whoosh(0.4, 5000, 400, rev=True), 14.45, 0.45)                       # fold into the dot
mix.add(bell(96, 1.0), 14.85, 0.16, verb=0.7); mix.add(blip(1600, 1100, 0.15), 14.85, 0.2)
mix.add(pad([48, 55, 60, 64, 67, 72], DUR - b(26), 3200, amp=0.22), b(26), 1.0, verb=0.5)  # resolve

mix.write("soundtrack.wav")
