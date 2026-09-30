# Energy — how to make it 炫酷, not just correct

Read this for every ad, promo or reel unless the user explicitly wants something calm.
The bar is the 15-second showreel (`assets/examples/showreel/`): a viewer should feel "how was that made?" within 2 seconds.
A clean layout that fades and slides in politely is a failure here, even if every rule is met.

## Why calm versions fail
They look like a slide deck with easing: one element per shot, flat background, text rising in,
long holds, soft transitions. Tasteful, readable — and scrolled past. Energy comes from density
(several things moving at once, in layers), rhythm (changes locked to the beat, faster in the drop),
impact (hits you can feel: shake + zoom punch + shockwave + flash + sound together), and variety
(a different technique every shot).

## The energy rules
1. **Never still.** Every frame has motion somewhere: background layer drifting (stripes, grid,
   field, rays), camera breathing, or type pulsing. `check.py motion` flags stills longer than 0.6 s.
2. **Three layers per shot.** Background texture (stripes / sunburst / field / tunnel), a hero
   element (big type, product, shape), and accents (shockwave, speed lines, labels, counters).
3. **Hits are stacked.** A key moment = `IMPACTS` shake + `ZOOMS` punch + `shockwave` + (optional)
   1–2 frame flash + a sound. Budget 5–8 hits in 20 s; the biggest on the drop and the logo.
4. **Cut on the beat, faster in the drop.** Hook: 2–4 changes in 2 s. Drop / feature montage:
   changes every beat, a burst of 8th-note cuts (0.25 s) somewhere. Average shot ≤ 1.5 s.
5. **Every word moves differently.** Use `kine()` styles in rotation: smear, spin, bounce, glitch,
   stroke, rise. Never the same style twice in a row. Headlines fill ≥ 70 % of the safe width (`fit`).
6. **Colour flips per cut.** Alternate background/foreground (brand dark ↔ accent ↔ light) so each
   cut reads as a new hit. The drop gets the loudest colour.
7. **One "how did they do that" moment** per 10 s: a 3D ring, a speed-ramped tunnel, a flow field
   that collapses into the next shot, a shape morph that becomes the next background (match cut),
   a counter racing up, a stamp slamming down.
8. **Transitions are events, not fades.** Use stripes, tear, slice, zoom, iris-from-an-object,
   match cuts (the element grows to fill the frame and becomes the next background). Never crossfade.
9. **Readable anyway.** Energy never excuses unreadable copy: the key line holds ≥ 0.8 s fully
   formed; decoration moves, the message lands and sits.

## Technique menu (engine functions)

| Job | Technique | Call |
|---|---|---|
| Hook | glitch slam, smear word, word-per-beat colour flips | `kine(..., 'glitch'|'smear')`, `slam`, bg swap |
| Pain / list | items slam with ✕ + buzz, shake per item | `kine('rise')`, `IMPACTS` |
| Reveal / drop | sunburst + shockwave + zoom punch + stamp | `sunburst`, `shockwave`, `ZOOMS`, `pop` |
| Numbers | racing counter, odometer-style | `counter(to, …)` |
| Features montage | 8th-note cuts, stripes background, dir alternating | `stripes(t, col, .08, ±1)` |
| Process | morphing shape per step with onion trail | `shapePts`, `morphPath`, `trail` |
| Scale / reach | flow field with beat shockwaves → vortex into next shot | `flowField({beats, vortex})` |
| Depth | speed-ramped tunnel + 3D text ring | `tunnel(rampZ(...))`, `ring3D` |
| Tech / data | scramble-decoding labels, HUD-lite numbers | `scramble` |
| CTA | pop + sheen sweep on the button, pulse on beats | `pop`, `sheen` |
| Transitions | stripes, tear, slice, zoom, iris, push, bars | `TRANS` types |

## Measured target
`python tools/check.py motion out/<name>_<fmt>.mp4` — the 15 s showreel measures median change ≈ 6
and 9 % still; a calm flat ad measured median 0.6 and 46 % still (and was rejected as 不炫酷).
Target: median ≥ 3, still ≤ 15 %, no still stretch ≥ 0.6 s. Run it on the first full render.

## Density check before rendering
Write it into docs/shotlist.md: for each shot, list layers (bg / hero / accents), the technique,
the hit (if any) and the sound. If a shot has one layer or no technique, redesign it.
