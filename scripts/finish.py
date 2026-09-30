"""Mux picture + sound into delivery files: two-pass loudnorm to -14 LUFS, light grain, yuv420p.

  python tools/finish.py --name 品牌_广告              # every out/frames_*.mp4 found
  python tools/finish.py --name promo --fmt 9x16 --grain 0 --lufs -16

Writes out/<name>_<fmt>.mp4 and out/soundtrack_norm.wav. Without soundtrack.wav it exports silent video.
"""
import argparse, json, pathlib, re, subprocess


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def loudnorm(src, dst, lufs, tp=-1.0):
    flt = f"loudnorm=I={lufs}:TP={tp}:LRA=11"
    r = run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", flt + ":print_format=json", "-f", "null", "-"])
    m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
    second = (f"{flt}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", second, "-ar", "48000", str(dst)])
    got, peak = measure(dst)
    # loudnorm can land off target on short clips (it drops out of linear mode); trim the rest with gain + limiter
    if got is not None and abs(got - lufs) > 0.3:
        tmp = dst.with_name(dst.stem + "_tmp.wav"); dst.replace(tmp)
        lim = 10 ** (tp / 20)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(tmp), "-af",
             f"volume={lufs - got:.2f}dB,alimiter=limit={lim:.3f}:level=false", "-ar", "48000", str(dst)])
        tmp.unlink()
        got, peak = measure(dst)
    print(f"audio: {m['input_i']} LUFS -> {got} LUFS, true peak {peak} dBFS")


def measure(path):
    r = run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"])
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--fmt", default="all")
    ap.add_argument("--audio", default="soundtrack.wav")
    ap.add_argument("--out", default="out")
    ap.add_argument("--lufs", type=float, default=-14)
    ap.add_argument("--grain", type=int, default=5, help="0 = off; 4-8 = subtle film grain")
    ap.add_argument("--crf", type=int, default=17)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    frames = sorted(out.glob("frames_*.mp4")) if a.fmt == "all" else [out / f"frames_{f}.mp4" for f in a.fmt.split(",")]
    audio = pathlib.Path(a.audio)
    norm = out / "soundtrack_norm.wav"
    if audio.exists():
        loudnorm(audio, norm, a.lufs)
    vf = (f"noise=c0s={a.grain}:c0f=t+u," if a.grain else "") + "format=yuv420p"
    for f in frames:
        fmt = f.stem.replace("frames_", "")
        dst = out / f"{a.name}_{fmt}.mp4"
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(f)]
        if audio.exists(): cmd += ["-i", str(norm)]
        cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-profile:v", "high",
                "-movflags", "+faststart"]
        cmd += ["-c:a", "aac", "-b:a", "256k", "-shortest"] if audio.exists() else ["-an"]
        cmd += [str(dst)]
        r = run(cmd)
        if r.returncode: print(r.stderr); continue
        info = run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0", str(dst)]).stdout.strip()
        print(f"{fmt}: {dst}  ({info})")


if __name__ == "__main__":
    main()
