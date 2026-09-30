---
name: motion-reel
description: Make motion-graphics videos rendered entirely from code — product ads, brand promos, launch videos, showreels, animated explainers, 抖音/视频号/小红书 竖屏广告, 宣传片, 片头, 动态海报视频 — with original beat-synced music, exported as MP4 in 9:16, 1:1 and 16:9 from one timeline. Use this whenever the user asks for a 动态视频, 广告视频, 宣传视频, 动效, motion graphics, showreel, promo/launch/ad video, or wants a company, product, PPT, PDF or website turned into a video, even if they don't say "motion" or name this skill. Also use it to revise such a video (change copy, cut a scene, retime, new format). Not for editing camera footage, and not for 硅基废话 whiteboard episodes (use guiji-feihua-video).
---

# Motion reel

Videos here are programs: `index.html` draws any frame from a time value, headless Chrome captures
every frame, ffmpeg encodes, and a Python synth writes a soundtrack on the same timeline. Because
every frame is a pure function of time, any change is an edit plus a re-render, and every format
comes from the same code.

The prompt is the small part. What makes these videos good is the harness: a real brief, a beat-grid
storyboard, springs instead of linear motion, sound on every hit, and looking at your own frames
until they are genuinely good.

## Environment

Needs Python with `playwright numpy scipy pillow`, ffmpeg on PATH, and Chrome or Edge installed
(Playwright launches the installed browser; no download). Check once with
`python -c "import playwright, numpy, scipy, PIL"` and `ffmpeg -version`; `pip install` what's missing.
On Windows set `PYTHONIOENCODING=utf-8` when a script prints Chinese.

Paths below: `<skill>` = this skill's folder. Scripts are copied into each project's `tools/`.

## Workflow

### 1. Gather facts before designing
Ask only for what you can't find. Sensible defaults: ads/promos 9:16 vertical first, 20–30 s;
showreels / résumé reels 16:9, 15 s (they are watched on a screen, and it is the genre's format);
synthesized music; the audience the material implies.

- **Source material** (URL, PPT, PDF, notes): extract the real text first (use the pptx/pdf skills;
  for a site, visit it and capture real screenshots, logo, colors). Pull brand colors and fonts from
  the material itself.
- **Write `docs/brief.md`**: audience, the one message they must remember, CTA/contact, brand look,
  and a list of every claim you intend to show with where it came from. Never invent numbers,
  guarantees or contact details — leave a CONFIG slot and tell the user it's empty.
- If the ad targets mainland China, read `references/compliance-cn.md` (education, medical and
  finance ads have hard rules about promising results).

### 2. Storyboard on the beat grid — with energy
Default to high energy (炫酷): users compare against a showreel, and a tidy but calm ad reads as a
slide deck and gets rejected. Go calm only when the user or the brand clearly asks for it.
Two finished projects set the quality bar: `assets/examples/showreel/` (the 15 s showreel, 9:16 + 16:9)
and `assets/examples/coffee-hype/` (a 20 s café opening ad). Skim their shotlist and scenes before
designing; borrow ideas, but build on the freshly scaffolded engine (the examples carry older engine copies).
Read `references/energy.md` and `references/storyboards.md` (the hype cut §7 layers onto any ad
pattern), and write `docs/shotlist.md`: time, shot, layers (bg / hero / accents), technique, hit,
on-screen text, transition, sound — on a beat grid: 120 BPM (beat = 0.5 s) by default, 128-140 for
hype cuts (set the same BPM in `CONFIG.BPM` and audio.py). Hook in the first 2 s, the core
message by ~30 % of the runtime, something new every 2–4 s, CTA in the last 3 s.
Write copy to the viewer in their own words (for students: "你", offer, 上岸; for parents: 孩子).
Share a compact version of the storyboard with the user in your reply; carry on building unless they
asked to approve it first or a key fact is missing.

### 3. Scaffold
```bash
python <skill>/scripts/new_project.py <project-dir> --dur 26 --title 片名
```
This creates `index.html` (engine + 3 demo scenes, duration already set), `audio.py`, `tools/`,
`docs/`, `CLAUDE.md`. Set the `C` palette and fonts, then replace everything between
`SCENES START` and `SCENES END` with your scenes. Write scene code with the Write/Edit tools rather
than shell heredocs — long JS in a heredoc breaks on quotes.

### 4. Build the scenes (index.html)
The engine already provides: springs (`sp(t,'snappy'|'def'|'heavy'|'playful')` — playful overshoots
≈21 %, leave room; `track()` for values with several targets), easings `E`, text helpers (`slam`,
`rise` per-character mask reveal, `T`, colored segments `[['拿到',C.ink],['offer',C.accent]]`,
`fit()` to shrink a line to a width), `poly(pts, p)` line-draw reveal, `pop()` scale-pop,
`mixHex`, backgrounds, camera shake `IMPACTS`, transitions `TRANS` (cut/push/iris/bars/wipe),
motion blur that densifies inside transitions and never crosses a cut, and multi-format layout `L`.
Fonts: `F_CJK` (Noto Sans SC), `F_SER` (Noto Serif SC, for food/culture/editorial brands — add it to
`FONT_FAMILIES`/`FONTS_TO_LOAD`), `F_LAT` (Bahnschrift). render.py warns if a family isn't installed.

- The FX library (section 5b) holds the showreel moves — use them, 2–3 per shot: `kine()` six
  kinetic-type styles (smear/spin/bounce/stroke/glitch/rise), `scramble`, `counter`, `shapePts` +
  `morphPath` + `trail`, `shockwave`, `sunburst`, `speedLines`, `tunnel(rampZ())`, `ring3D`,
  `flowField` (beat shockwaves, dots, vortex), `stripes`, `sheen`; `ZOOMS` camera punches next to
  `IMPACTS` shake; transitions stripes/tear/slice/zoom besides iris/push/bars/wipe/cut;
  `along()` rides an object on a `poly()` route; `ring3D({occluder})` wraps text around a hero object.
- Fill backgrounds with `fillBg()` (overscans the frame) so shake, zoom punches and transitions never
  expose an edge. Add `{at, type:'cut'}` to `TRANS` for every cut inside a scene (montages).
- Scenes are `draw(t)` with **global** time; list them in `SCENES` and their boundaries in `TRANS`.
- Size everything in `L.u` and place relative to `L.cx`, `L.cy`, `L.safe` so 1:1 and 16:9 work.
  Keep key content inside `L.safe` (vertical apps cover the top and bottom).
- The incoming scene must already be animating while its transition plays — otherwise the
  transition reveals an empty frame.
- Avoid the AI-video look: centered title on a gradient, everything fading in, corner labels and
  frame borders, glow, generic particles. One accent color. Big type with real hierarchy.
- Keep it deterministic: no `Math.random`, timers or carried state (use `hr(n)`).

### 5. Look at it (critique loop)
Read `references/critique.md`. Render one still per beat plus every transition, make contact
sheets, and actually open and look at every page:
```bash
python tools/render.py --every 0.5 --trans        # out/stills_9x16/ and out/trans_9x16/
python tools/check.py sheet out/stills_9x16       # paged, 12 frames per page
python tools/check.py sheet out/trans_9x16
python tools/render.py --stills 3.2,3.4 --noblur  # sharp frames when judging a collision
```
Score the 8 criteria (energy included), fix the three worst problems, repeat until all are 8+. Check other formats
with `--fmt all --every 1` if they're being delivered.

### 6. Score the soundtrack (audio.py)
List every visual event with its time (slams, transitions, impacts, list items, the logo) and give
each a sound. Shape sections with the story: sparse/minor under the problem, riser into the turn,
drop to a bright major progression on the core message, resolve on the end card. `audio_lib.py`
has kick/clap/hat/snare/tick, pluck/bell/piano/pad/bass, blip/buzz/coin/whoosh/riser/impact/glitch,
and a `Mixer` with sidechain and reverb. The mix is normalized to its loudest peak, so a quiet
section needs noticeably bigger gains. Verify with `python tools/check.py sections soundtrack.wav`
(RMS per 0.5 s; flags dead patches — the hook must never be one) and `check.py spec`.

### 7. Render, finish, verify
```bash
python audio.py
python tools/render.py --fmt 9x16            # or all; ~25 s per 6 s of 1080p60 on a laptop
python tools/finish.py --name 片名            # -14 LUFS two-pass loudnorm, grain, yuv420p
python tools/check.py at out/片名_9x16.mp4 <every cut and transition time>
python tools/check.py phone out/片名_9x16.mp4
python tools/check.py motion out/片名_9x16.mp4   # energy: median ≥ 3, still ≤ 15 %, no still ≥ 0.6 s
```
If `motion` is below target, fix the flagged stretches (background motion, pulses, earlier cuts)
and re-render — that number is how the user's "不炫酷" shows up in data.
Run long renders in the background and do the audio or checks meanwhile.

### 8. Deliver
Send the MP4 (SendUserFile when available). Reply with: a short scene/time table, what the music does,
claims or placeholders the user must confirm (contact info, prices, promises vs. contract), and the
one command to re-render. Delete bulky intermediates (stills/trans/picks folders, frames_*.mp4)
but keep `index.html`, `audio.py`, `tools/`, `docs/`, `soundtrack.wav` and the final check sheets in
`out/check/` so edits stay cheap and the review is traceable.

## Revisions

Users usually come back with copy changes, a removed scene, or a new length.
- **Copy/number change**: edit the strings everywhere they appear (grep the old text), re-check the
  affected stills, full render, finish. Overwrite the delivered file and remove superseded versions
  so the wrong one can't be posted.
- **Remove a scene** (e.g. 21–25 s): don't retime everything. Remap time in the engine
  (`const story = t => t >= 21 ? t + 4 : t;`), replace the two transitions around it with one,
  shorten `DUR`, and in audio.py delete that section and set `mix.shift = -4` before the later sections.
- **Removing a disclaimer the user asked to drop**: do it, then say in one line what that changes
  for compliance and where the condition still appears.

## Lessons that cost a re-render

- Motion blur across a hard cut makes a ghosted double frame → cuts go in `TRANS` as `type:'cut'`.
- Very fast push/iris with 5 blur samples shows stepped copies or a grey wash → the engine raises
  samples inside transitions; also prefer `inOutCubic` over `inOutExpo` for big moves.
- In a panel push, both panels must move together (in and out centred on the same boundary).
- White flashes over dark scenes look muddy grey; use 2–4 frames and rarely.
- Load every font weight before capture (render.py does it via `META.FONTS`); CJK default is Noto
  Sans SC (free for commercial use), Latin display Bahnschrift.
- Stamps, badges and docked headlines collide easily — check the frames where things move into place.
- Things entering from off-screen can peek into the frame during a neighbouring transition; pop them
  in by scale at their resting place instead of flying them long distances.
- Iris edge rings and glows smear into a muddy halo under the transition blur; prefer a clean edge.
- A hard cut must land on a frame that already has content — start the next scene 0.1–0.2 s early.
- Offsets like `L.cy - 380 * U` are sized for a 1920-tall frame and fall off a 1080-tall one. Give
  stacked shots a landscape branch from the start (`const LAND = !L.vert`; word left at `W*.29`,
  demo right at `W*.68`) so a later "also give me 16:9" is a re-render, not a rewrite.
