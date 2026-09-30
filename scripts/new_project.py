"""Scaffold a motion-reel project.

  python <skill>/scripts/new_project.py D:/path/to/项目名 [--dur 20] [--title 片名]

Creates:
  index.html      engine + demo scenes (replace the scenes, keep the engine)
  audio.py        soundtrack on the same timeline
  tools/          render.py, finish.py, check.py, audio_lib.py (copied, so the project is self-contained)
  docs/brief.md   facts, audience, message, claims to verify
  docs/shotlist.md beat-grid storyboard
  CLAUDE.md       house rules
"""
import argparse, pathlib, re, shutil, sys

SKILL = pathlib.Path(__file__).resolve().parent.parent

BRIEF = """# Brief — {title}

- 产品 / 品牌：
- 来源材料（网址 / PPT / PDF）：
- 目标观众：
- 投放平台与画幅：9:16（主）/ 1:1 / 16:9
- 时长：{dur}s
- 一句话核心信息（观众看完要记住什么）：
- 行动号召（CTA）与联系方式：
- 品牌色 / 字体 / logo：
- 参考（风格帧、视频、图库）：
- 音乐：合成（默认）/ 提供的曲目

## 需要用户确认的说法（原文出处）
-

## 合规提示（行业、地区）
-
"""

SHOTLIST = """# Shot list — {title}  ({dur}s · 120 BPM · 1 beat = 0.5s)

| 时间 | 镜头 | 画面 / 文字 | 转场 | 声音 |
|---|---|---|---|---|
| 0.0–2.0 | 钩子 | 前 2 秒最抓人的画面 + 5 字以内大字 | cut | 冲击 |
|  |  |  |  |  |
| 末 3s | 品牌收尾 | logo + CTA |  | 主和弦 |
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--dur", type=float, default=20)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    d = pathlib.Path(a.dir)
    if (d / "index.html").exists():
        sys.exit(f"{d / 'index.html'} already exists — not overwriting")
    title = a.title or d.name
    (d / "tools").mkdir(parents=True, exist_ok=True)
    (d / "docs").mkdir(exist_ok=True)
    for f in ["render.py", "finish.py", "check.py", "audio_lib.py"]:
        shutil.copy(SKILL / "scripts" / f, d / "tools" / f)
    html = (SKILL / "assets" / "engine.html").read_text(encoding="utf-8")
    dur = int(a.dur) if a.dur == int(a.dur) else a.dur
    html = re.sub(r"TITLE: '[^']*'", f"TITLE: '{title}'", html)
    html = re.sub(r"DUR: [\d.]+,", f"DUR: {dur},", html)
    html = html.replace("<title>motion-reel</title>", f"<title>{title}</title>")
    (d / "index.html").write_text(html, encoding="utf-8")
    audio = (SKILL / "assets" / "audio_template.py").read_text(encoding="utf-8")
    (d / "audio.py").write_text(re.sub(r"DUR, BPM = [\d.]+,", f"DUR, BPM = {float(a.dur)},", audio), encoding="utf-8")
    if not (d / "CLAUDE.md").exists():
        shutil.copy(SKILL / "assets" / "CLAUDE.md", d / "CLAUDE.md")
    (d / "docs" / "brief.md").write_text(BRIEF.format(title=title, dur=a.dur), encoding="utf-8")
    (d / "docs" / "shotlist.md").write_text(SHOTLIST.format(title=title, dur=a.dur), encoding="utf-8")
    print(f"project ready: {d.resolve()}")
    print(f"duration set to {dur}s in index.html and audio.py; the demo scenes/cues cover the first 6s — replace them")


if __name__ == "__main__":
    main()
