"""Review helpers — look at these images before showing anything to the user.

  python tools/check.py sheet out/stills_9x16             # contact sheet(s) of a stills folder
  python tools/check.py sheet out/promo_9x16.mp4 --every 0.5
  python tools/check.py at out/promo_9x16.mp4 2.0,9.0,14.95  # exact frames (cuts, transition midpoints)
  python tools/check.py strip out/promo_9x16.mp4 --at 4.2    # 12 consecutive frames around a fast move
  python tools/check.py phone out/promo_9x16.mp4             # 360px-wide readability test, 1 fps
  python tools/check.py motion out/promo_9x16.mp4            # finds stretches where nothing moves (≥0.6 s)
  python tools/check.py sections soundtrack.wav              # loudness per 0.5 s — finds dead patches
  python tools/check.py loud out/promo_9x16.mp4              # integrated LUFS + true peak
  python tools/check.py spec soundtrack.wav                  # spectrogram

Sheets are paged (default 12 frames per page) so each cell stays large enough to judge when an
image viewer downsizes the page. Output goes to <out>/check/ and every written path is printed.
"""
import argparse, math, pathlib, re, subprocess, wave
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def label_font(size):
    for f in ("arial.ttf", "DejaVuSans.ttf", "Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try: return ImageFont.truetype(f, size)
        except OSError: continue
    return ImageFont.load_default()


def ff(*args):
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def pages(images, labels, stem, out, per=12, cell=None):
    """Write paged contact sheets: <out>/<stem>_p1.png ... (or <stem>.png when one page)."""
    if not images: raise SystemExit("nothing to tile")
    w0, h0 = images[0].size
    vertical = h0 > w0
    cw = cell or (300 if vertical else 480)
    ch = int(cw * h0 / w0)
    cols = min(per, 6 if vertical else 4, len(images))
    fnt = label_font(max(16, cw // 12))
    n_pages = math.ceil(len(images) / per)
    out.mkdir(parents=True, exist_ok=True)
    for pg in range(n_pages):
        chunk = list(zip(images, labels))[pg * per:(pg + 1) * per]
        rows = math.ceil(len(chunk) / cols)
        sheet = Image.new("RGB", (cols * cw, rows * ch), (60, 60, 60))
        for i, (im, lb) in enumerate(chunk):
            im = im.convert("RGB").resize((cw, ch), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, fnt.getlength(lb) + 12, fnt.size + 10], fill=(0, 0, 0))
            d.text((6, 4), lb, fill=(255, 70, 70), font=fnt)
            sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
        dst = out / (f"{stem}.png" if n_pages == 1 else f"{stem}_p{pg + 1}.png")
        sheet.save(dst); print(dst)


def frames_from_video(video, times, tmp):
    tmp.mkdir(parents=True, exist_ok=True)
    ims = []
    for i, t in enumerate(times):
        p = tmp / f"{i:03d}.png"
        ff("-ss", f"{t}", "-i", str(video), "-frames:v", "1", str(p))
        if p.exists(): ims.append(Image.open(p).copy())
    return ims


def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def read_audio(path):
    if str(path).lower().endswith(".wav"):
        with wave.open(str(path)) as w:
            sr, ch = w.getframerate(), w.getnchannels()
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return x.reshape(-1, ch).mean(1), sr
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768, 48000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sheet", "at", "strip", "phone", "motion", "sections", "loud", "spec"])
    ap.add_argument("src")
    ap.add_argument("times", nargs="?")
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--at", type=float)
    ap.add_argument("--per", type=int, default=12, help="frames per sheet page")
    ap.add_argument("--cell", type=int, help="cell width in px")
    ap.add_argument("--out", default="out")
    ap.add_argument("--thr", type=float, default=0.6, help="motion: stillness threshold")
    ap.add_argument("--quiet", type=float, default=9, help="sections: dB under median counted as quiet")
    a = ap.parse_args()
    src = pathlib.Path(a.src)
    OUT = pathlib.Path(a.out) / "check"
    tmp = OUT / "_tmp"
    # unique stem from the path, so out/stills_9x16 and out/x/stills_9x16 don't overwrite each other
    stem = "_".join(p for p in src.with_suffix("").parts[-2:] if p not in (".", "out"))

    if a.cmd == "sheet":
        if src.is_dir():
            files = sorted(src.glob("*.png"))
            pages([Image.open(f) for f in files], [f.stem.lstrip("t") for f in files], f"sheet_{stem}", OUT, a.per, a.cell)
        else:
            d = duration(src); ts = [round(i * a.every, 3) for i in range(int(d / a.every) + 1) if i * a.every < d]
            pages(frames_from_video(src, ts, tmp), [f"{t:.2f}" for t in ts], f"sheet_{stem}", OUT, a.per, a.cell)
    elif a.cmd == "at":
        ts = [float(x) for x in a.times.split(",")]
        pages(frames_from_video(src, ts, tmp), [f"{t:.3f}" for t in ts], f"at_{stem}", OUT, a.per, a.cell or 420)
    elif a.cmd == "strip":
        fps = 60; ts = [a.at + (k - 6) / fps for k in range(12)]
        pages(frames_from_video(src, ts, tmp), [f"{t:.3f}" for t in ts], f"strip_{stem}_{a.at}", OUT, 12, a.cell)
    elif a.cmd == "phone":
        # ~360 px wide is how a phone feed shows a vertical video — can a stranger still read every line?
        d = duration(src); ts = [float(i) + 0.5 for i in range(int(d))]
        pages(frames_from_video(src, ts, tmp), [f"{t:.1f}" for t in ts], f"phone_{stem}", OUT, 10, 360)
    elif a.cmd == "sections":
        x, sr = read_audio(src)
        win = int(sr * a.every); n = len(x) // win
        db = [20 * np.log10(np.sqrt(np.mean(x[i * win:(i + 1) * win] ** 2)) + 1e-9) for i in range(n)]
        med = float(np.median(db))
        print(f"RMS per {a.every}s (median {med:.1f} dB). '<- quiet' = more than 9 dB below median")
        for i, v in enumerate(db):
            bar = "#" * max(0, int((v + 40) / 1.5))
            print(f"{i * a.every:6.2f}s {v:6.1f} dB {bar}{'   <- quiet' if v < med - a.quiet else ''}")
        print("(a deliberate breath before a drop can sit 6-10 dB under the median for <= 0.5 s; the hook never should)")
    elif a.cmd == "motion":
        # mean frame-to-frame change at 10 fps on a 120px-wide greyscale copy (grain averages away)
        d = duration(src)
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", "fps=10,scale=120:-2,format=gray",
                            "-f", "rawvideo", "-"], capture_output=True)
        w, h = 120, None
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip().split(",")
        h = int(round(int(probe[1]) * 120 / int(probe[0]) / 2) * 2)
        fr = np.frombuffer(r.stdout, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)
        diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
        thr = a.thr
        still, runs, start = diff < thr, [], None
        for i, s_ in enumerate(list(still) + [False]):
            if s_ and start is None: start = i
            if not s_ and start is not None:
                if (i - start) / 10 >= 0.6: runs.append((start / 10, i / 10))
                start = None
        print(f"motion: mean change {diff.mean():.2f}/255 per 0.1 s, median {np.median(diff):.2f}; "
              f"still (< {thr}) {still.mean() * 100:.0f}% of the time")
        for s0, s1 in runs: print(f"  STILL {s0:5.1f}s – {s1:5.1f}s ({s1 - s0:.1f}s): add background motion, a pulse or cut sooner")
        if not runs: print("  no still stretch ≥ 0.6 s")
        ok = np.median(diff) >= 3 and still.mean() <= .15 and not runs
        print(f"  energy target (the showreel: median ≈ 6, still ≈ 9 %): median ≥ 3, still ≤ 15 %, no still run → "
              f"{'PASS' if ok else 'BELOW TARGET — see references/energy.md'}")
    elif a.cmd == "loud":
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
        print(f"integrated {i[-1] if i else '?'} LUFS (target -14), true peak {p[-1] if p else '?'} dBFS (keep <= -1)")
    elif a.cmd == "spec":
        OUT.mkdir(parents=True, exist_ok=True); dst = OUT / f"spec_{stem}.png"
        ff("-i", str(src), "-lavfi", "showspectrumpic=s=1500x300:legend=1:scale=log:fscale=log", str(dst)); print(dst)


if __name__ == "__main__":
    main()
