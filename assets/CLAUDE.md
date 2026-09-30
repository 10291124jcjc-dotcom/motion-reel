# Motion studio rules

These rules apply to every video in this project. The /motion-reel skill has the full workflow.

## Render contract
- The film is a pure function of time: `render(t)` in index.html paints frame t. No CSS transitions,
  no setTimeout/requestAnimationFrame in capture mode, no state carried between frames, no `Math.random`
  (use `hr(n)` or seeded noise). Same input → same frame, every run.
- Scenes receive the global time. Motion uses closed-form springs (`sp`, `track`) or the easings in `E`.
- Lay out with `L` (units `L.u`, `L.cx/L.cy`, `L.safe`) so 9:16, 1:1 and 16:9 all come from one timeline.
  Use `fit()` for any line that might overflow a narrow format.

## Look
- Avoid the AI-video defaults: a centered title on a gradient, everything fading in, corner labels
  and frame borders, glow on UI chrome, generic particle bursts.
- One display face and one UI face; one accent color unless the brand needs more.
- Every 2–4 seconds something new must happen. Hook in the first 2 seconds.
- Minimum text size at 1080 short edge: 36px for body, 24px for fine print.

## Sound
- Score and SFX are synthesized in audio.py on the same timeline unless a track is supplied.
- Every slam, transition and impact gets a sound. Final loudness -14 LUFS (finish.py does it).

## Before showing anything
1. Stills at every beat + every transition midpoint → contact sheet → look at it.
2. Score 1–10: hook, readability at phone size, motion quality, variety, composition, brand accuracy, sound sync.
3. Fix the 3 worst problems, re-check. Repeat until every score is 8+.
4. Full render → finish → check exact frames at cuts in the final MP4.

## Commands
    python audio.py                      # soundtrack.wav
    python tools/render.py --every 0.5 --trans   # beat + transition stills (--fmt all for every format)
    python tools/check.py sheet out/stills_9x16  # paged contact sheets -> out/check/
    python tools/check.py sections soundtrack.wav
    python tools/render.py --fmt all     # full frames
    python tools/finish.py --name <片名>  # -14 LUFS, grain, yuv420p  -> out/<片名>_<fmt>.mp4
