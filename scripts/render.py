"""Capture a seek(t) page frame-by-frame in headless Chrome and encode it.

Run from the project root (the folder that holds index.html):

  python tools/render.py                      # full render, 9x16  -> out/frames_9x16.mp4
  python tools/render.py --fmt all            # 9x16, 1x1 and 16x9
  python tools/render.py --every 0.5          # one still per beat       -> out/stills_9x16/
  python tools/render.py --trans              # every TRANS entry at -0.1/0/+0.1 s -> out/trans_9x16/
  python tools/render.py --stills 0.5,2.1     # chosen times             -> out/picks_9x16/
  python tools/render.py --every 0.5 --noblur # sharp stills for judging layout
  python tools/render.py --det 3.2            # determinism check: render t twice, compare hashes

Each still mode has its own folder, so running one never wipes another.
The page must expose window.render(t, blur) and window.META = {W, H, FPS, DUR, FONTS, TRANS}.
The video intermediate is near-lossless (yuv444, CRF 12); finish.py makes the delivery encode.
"""
import argparse, base64, hashlib, pathlib, subprocess, sys, time
from playwright.sync_api import sync_playwright

FORMATS = ["9x16", "1x1", "16x9"]
ERRORS = []  # page JS errors — a throwing scene would otherwise render blank or stale frames silently


def check_errors(where):
    if ERRORS:
        print(f"JS ERROR at {where}: " + " | ".join(dict.fromkeys(ERRORS))[:600], flush=True)
        sys.exit(1)


def launch(p):
    for ch in ("chrome", "msedge", None):  # prefer an installed browser; no download needed
        try:
            return p.chromium.launch(channel=ch, headless=True) if ch else p.chromium.launch(headless=True)
        except Exception:
            continue
    sys.exit("No Chromium found. Install Chrome, or run: python -m playwright install chromium")


def open_page(browser, html, fmt):
    page = browser.new_page(viewport={"width": 480, "height": 480})
    page.on("pageerror", lambda e: ERRORS.append(str(e)))
    page.on("console", lambda m: ERRORS.append(m.text) if m.type == "error" else None)
    page.add_init_script("window.__CAPTURE__ = true;")
    page.goto(pathlib.Path(html).resolve().as_uri() + f"?fmt={fmt}")
    page.wait_for_function("window.META !== undefined")
    page.evaluate("""async () => {
        for (const f of (window.META.FONTS || [])) await document.fonts.load(f);
        await document.fonts.ready;
    }""")
    missing = page.evaluate("window.missingFonts ? window.missingFonts() : []")
    if missing:
        print(f"WARNING: fonts not installed, Chrome is using a fallback: {', '.join(missing)}", flush=True)
    return page, page.evaluate("window.META")


def grab(page, t, blur=True):
    js = f"(() => {{ render({t}, {'true' if blur else 'false'}); return document.getElementById('c').toDataURL('image/png'); }})()"
    return base64.b64decode(page.evaluate(js).split(",", 1)[1])


def stills(page, times, folder, blur):
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.png"): old.unlink()
    for t in times:
        (folder / f"t{t:06.3f}.png").write_bytes(grab(page, t, blur))
        check_errors(f"t={t}")
    return len(times)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--fmt", default="9x16", help="9x16 | 1x1 | 16x9 | comma list | all")
    ap.add_argument("--out", default="out")
    ap.add_argument("--stills", help="comma-separated times in seconds -> picks_<fmt>/")
    ap.add_argument("--every", type=float, help="one still every N seconds -> stills_<fmt>/")
    ap.add_argument("--trans", action="store_true", help="each transition at -0.1/0/+0.1 s -> trans_<fmt>/")
    ap.add_argument("--noblur", action="store_true", help="stills without motion blur (layout review)")
    ap.add_argument("--det", type=float, help="determinism check at time t")
    a = ap.parse_args()
    fmts = FORMATS if a.fmt == "all" else a.fmt.split(",")
    out = pathlib.Path(a.out); out.mkdir(exist_ok=True)
    blur = not a.noblur

    with sync_playwright() as p:
        browser = launch(p)
        for fmt in fmts:
            page, meta = open_page(browser, a.html, fmt)
            dur = meta["DUR"]
            if a.det is not None:
                h1 = hashlib.md5(grab(page, a.det)).hexdigest()
                grab(page, a.det / 2)  # disturb state in between
                h2 = hashlib.md5(grab(page, a.det)).hexdigest()
                print(f"[{fmt}] t={a.det}: {'OK deterministic' if h1 == h2 else 'FAIL frames differ'} ({h1[:8]} / {h2[:8]})")
                continue
            if a.every or a.stills or a.trans:
                if a.every:
                    ts = [round(i * a.every, 3) for i in range(int(dur / a.every) + 1) if i * a.every < dur]
                    print(f"[{fmt}] {stills(page, ts, out / f'stills_{fmt}', blur)} stills -> {out / f'stills_{fmt}'}")
                if a.trans:
                    ts = sorted({round(min(max(tr['at'] + d, 0), dur - 1e-3), 3)
                                 for tr in meta.get("TRANS", []) for d in (-0.1, 0.0, 0.1)})
                    print(f"[{fmt}] {stills(page, ts, out / f'trans_{fmt}', blur)} transition stills -> {out / f'trans_{fmt}'}")
                if a.stills:
                    ts = [float(x) for x in a.stills.split(",")]
                    print(f"[{fmt}] {stills(page, ts, out / f'picks_{fmt}', blur)} stills -> {out / f'picks_{fmt}'}")
                continue
            fps = meta["FPS"]
            n = int(round(fps * dur))
            dst = out / f"frames_{fmt}.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
                                   "-c:v", "png", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                                   "-pix_fmt", "yuv444p", str(dst)], stdin=subprocess.PIPE)
            t0 = time.time()
            for i in range(n):
                ff.stdin.write(grab(page, i / fps))
                if ERRORS: ff.stdin.close(); ff.wait(); check_errors(f"frame {i} (t={i / fps:.3f})")
                if i % (fps * 2) == 0:
                    print(f"[{fmt}] frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
            ff.stdin.close(); ff.wait()
            print(f"[{fmt}] done -> {dst} ({n} frames, {time.time() - t0:.0f}s)")
        browser.close()


if __name__ == "__main__":
    main()
