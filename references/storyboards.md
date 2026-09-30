# Storyboard patterns

Pick the pattern that matches the request, then write docs/shotlist.md on the beat grid
(120 BPM → 1 beat = 0.5 s, 1 bar = 2 s). Put cuts and big moments on beats, downbeats for the biggest.

## Contents
1. Showreel (10–20 s) — "show what you can do"
2. Product / service ad (20–30 s, 9:16) — the default for anything being sold
3. Offer-led ad (e.g. 先培训后付费) — when one commercial idea is the whole point
4. Local shop / opening promo (15–20 s) — cafés, restaurants, stores, gyms
5. UI state morph (15–25 s) — software products
6. Story / history (30–90 s)
7. Hype cut (any ad, 15–25 s) — the 炫酷 structure; layer it onto 2–4 when energy matters (default)

---

## 1. Showreel (15 s, 16:9)
Genre rules: a new technique every shot, best first, bookend open and close.

| t | shot | technique |
|---|---|---|
| 0–1.5 | dot → line → tear open | minimal, precise timing |
| 1–3.5 | 4–5 words, one per beat | kinetic type, each word a different move |
| 3.5–6.5 | shape morph on beat + easing graph | form & timing |
| 6.5–9 | generative field, shockwave per beat → vortex | systems |
| 9–11 | speed-ramped tunnel + 3D text ring | depth |
| 11–12.5 | 8th-note cuts with counters | rhythm edit |
| 12.5–15 | stripes collapse → logo lockup → dot out | identity, bookend |

## 2. Product / service ad (20–30 s, 9:16 first)

| t | beat | content |
|---|---|---|
| 0–3 | Hook | the viewer's pain as a question, ≤ 8 characters per line, slams |
| 3–7 | Problem | make the pain concrete: a checklist of obstacles each getting a ✕ |
| 7–9 | Turn | color flips, one line that reframes ("别急着交钱") + riser |
| 9–15 | Offer (the drop) | the core promise huge, then 3 steps of how it works |
| 15–21 | Proof / what you get | numbers from the source, service list, capabilities grid |
| 21–23 | How to start | 3–5 numbered steps |
| last 3 | End card | logo, one-line positioning, CTA button, contact |

Music: minor & sparse under the problem, build in the turn, drop to major at the offer,
resolve on the logo. Error buzz on each ✕, coin/ding on "payment" moments, pops on list items.

Viewer is the subject: write "你" to the target audience in their words (students: offer / 上岸 /
边训边投; parents: 孩子 / 稳定 / 保障). Pull every phrase from the source, then shorten.

## 3. Offer-led ad
When the whole ad exists to land one commercial idea (先培训后付费, 零首付, 7 天无理由):
- Say it by 30 % of the runtime, as the biggest type in the film, on the music drop.
- Show the mechanism as a sequence (① 前期 ¥0 → ② 培训 → ③ 录用通知 → 付费) with a coin that
  only lands on the last step — the viewer should understand it without reading.
- Add the condition in fine print on the same screen (需通过评估、以协议为准).

## 4. Local shop / opening promo (20 s, 9:16)

| t | beat | content |
|---|---|---|
| 0–2 | Audience callout | name the people nearby in their slang (早八人 / 打工人) + a product icon already moving at t=0 |
| 2–4 | Reveal | "X 新开了一家" → brand name slam |
| 4–8 | Offer (drop, by 20–30 %) | the deal huge (第二杯 / 半价), mechanism as picture (2 cups, stamp on the 2nd), dates, fine print |
| 8–11 | Origin | where it comes from, a route line drawn with `poly()` |
| 11–14 | Craft | the process that makes it better (现烘, 手作), sensory line |
| 14–17 | Place | street, pin drop, "顺路一杯" |
| 17–20 | End card | mark, name, one-line positioning, CTA pill with the offer + dates, address |

Promo fine print: period, conditions, "活动规则以门店公示为准" (see compliance-cn.md).

## 5. UI state morph (software)
One container never cuts; it morphs button → field (typed) → loader → check → card → chart → toast → logo.
A cursor drives every change. Last frame equals the first so it loops. Use `track()` for values that
change target many times; text inside a morphing box enters after the morph starts and leaves before
the next. Use real screenshots/data from the product URL, never invented UI.

## 6. Story / history
Acts with timestamps, a visual payoff every 3–5 s, a recurring motif (a dot, a line, a character)
that carries through cuts. Captions sized like subtitles unless a line is the payoff. Longer pieces:
build stills for every shot first, then an animatic at half resolution, then polish.

## 7. Hype cut (20 s, 9:16) — showreel energy applied to an ad

| t | shot | layers & technique | hit |
|---|---|---|---|
| 0–0.3 | cold open | product/brand shape already moving, glitch-slam first word | shake |
| 0.3–2 | hook | 3 words on 3 beats, each a different `kine` style, bg colour flips per word | punch on word 3 |
| 2–2.4 | transition | tear or slice | whoosh |
| 2.4–4 | brand reveal | name smear-in over sunburst, scramble subline | shockwave |
| 4–8 | THE OFFER (drop) | giant type spin-in, stamp slam, counter racing, sunburst + stripes behind | shake + zoom + flash |
| 8–10 | 8th-note montage | 6–8 cuts of features/benefits, stripes dir alternating, colour flip each cut | tick per cut |
| 10–13 | wow moment | tunnel / 3D ring / flow field → vortex that becomes the next shot | riser → hit |
| 13–16 | proof / place | route `poly()` draw, pin drop with shockwave, counters | pops |
| 16–17 | build | everything collapses to a line / point (bookend) | reverse swell |
| 17–20 | end card | logo pops with shockwave, name kine-spin, CTA pop + sheen, beat pulses | biggest hit |

Music: 128–140 BPM feels more urgent than 120 for hype cuts; keep the drop at the offer.
