# Critique loop

Read this before the first review pass and whenever a round of fixes is done.

You wrote the code, so you will see what you meant to draw. Look at the rendered images as a
harsh motion director would, not as the author.

## What to render for review

| When | Command | Why |
|---|---|---|
| Before audio / full render | `render.py --every 0.5` + `check.py sheet out/stills_<fmt>` | one frame per beat: pacing, layout, dead beats |
| Every transition | `render.py --trans` + `check.py sheet out/trans_<fmt>` | overlaps, stepped ghosts, empty reveals |
| Judging a collision | `render.py --stills a,b --noblur` | blur hides exact edges |
| Other formats | `render.py --fmt all --every 1` | text overflow and cramped layouts in 1:1 / 16:9 |
| After finish | `check.py at final.mp4 <cut times>` | grain/encode didn't break anything; exact cut frames |
| Fast moves | `check.py strip final.mp4 --at <t>` | 12 consecutive frames: pops, jitter, one-frame glitches |
| Phone | `check.py phone final.mp4` | at 360px wide, can a stranger still read every line? |
| Energy | `check.py motion final.mp4` | median change ≥ 3, still ≤ 15 %, no still stretch ≥ 0.6 s |
| Sound | `check.py sections soundtrack.wav`, `check.py spec`, `check.py loud out/<name>_<fmt>.mp4` | no dead patches (esp. the hook), hits land on picture changes, -14 LUFS |

## Score 1–10 (write the scores down, fix until every one is 8+)

1. **Hook** — does the first 2 s stop a scroll? A question, a conflict, a bold claim, a striking image.
2. **Readability** — every line readable at phone size and on screen long enough (≈ 0.25 s per CJK
   character, minimum ~0.8 s for a headline). Contrast holds on every background it crosses.
3. **Motion quality** — things accelerate and settle (springs), nothing slides linearly, no dead frames,
   no stepped ghosts in fast transitions, blur never spans a hard cut.
4. **Variety** — something new every 2–4 s; no two consecutive shots use the same move.
5. **Composition** — clear focal point per shot, inside the safe area, nothing colliding.
6. **Brand / message accuracy** — real colors, real names, claims match the source material exactly.
7. **Sound sync** — every slam, cut and impact has a sound; music sections change with the story.
8. **Energy / wow** — would it hold its own next to the 15 s showreel? Layers per shot, a technique
   per shot, stacked hits, beat-locked cuts, no still stretch (`check.py motion` passes). See energy.md.

## Hunt list (things that repeatedly went wrong)

- Text overlapping another element during a swap or a dock animation (e.g. a stamp over a headline).
- A transition revealing an incoming scene whose animation hasn't started yet → empty frames.
- Two panels in a push not moving together (one arrives before the other leaves → both overlap).
- Very fast iris/push with too few blur samples → a flat grey wash or stepped copies.
- White flash frames over a dark scene read as muddy grey — keep flashes ≤ 4 frames and rare.
- Iris edge rings / glows under transition blur become a brownish halo — the "glow" AI look.
- Elements flying in from off-screen peeking into the frame during an adjacent transition.
- Frame 0 nearly empty — the first thing should already be moving at t = 0.
- Big playful overshoot (≈21 %) pushing an element into a neighbour.
- Motion blur averaging two different shots at a hard cut (ghost double exposure).
- Chips/labels running past the right edge in 9:16, or a headline overflowing in 16:9 → use `fit()`.
- Corner labels, frame borders, centered-title-on-gradient, everything fading in: the AI-video look.
- Placeholder text left in (电话 ____, lorem, "品牌名称").
- A number/claim that isn't in the source material.

## Fix discipline

Fix the 3 worst problems, re-render only the affected stills, look again. Then full render.
After the final encode, spot-check exact frames at every cut and transition midpoint in the MP4.
