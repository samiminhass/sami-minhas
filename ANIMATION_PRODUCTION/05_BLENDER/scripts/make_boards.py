"""Builds storyboard panels, a contact sheet, a shot list and a timed animatic from blockout renders.

Usage: python3 make_boards.py SHOTS.json RENDER_DIR OUT_ROOT
Writes OUT_ROOT/03_STORYBOARDS/<ID>_<Title>/, OUT_ROOT/04_ANIMATICS/, OUT_ROOT/02_PREPRODUCTION/shotlists/.
"""
import json
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SR = 48000

# Approximate UI overlay zones shared by Shorts, TikTok and Reels, as fractions of a 9:16 frame.
# Planning aid only; verify against each platform's current guidance before final export.
UI_ZONES = [(0.0, 0.0, 1.0, 0.10), (0.0, 0.78, 1.0, 1.0), (0.86, 0.45, 1.0, 0.78)]

GRADES = {
    "night": (np.array([0.42, 0.45, 0.70]), 0.0),
    "dawn": (np.array([0.88, 0.92, 1.05]), 0.0),
    "morning": (np.array([1.08, 1.0, 0.86]), 0.03),
    "day": (np.array([1.0, 1.0, 1.0]), 0.0),
}


def grade(img, name):
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    mul, lift = GRADES.get(name, GRADES["day"])
    if name == "night":
        # Workbench has no emission, so warm practicals (oven mouth, fresh bread) are kept bright by hue.
        glow = (a[..., 0] > 0.35) & (a[..., 0] > 1.3 * a[..., 1]) & (a[..., 0] > 2.2 * a[..., 2])
        out = a * mul
        out[glow] = np.clip(a[glow] * np.array([1.9, 1.3, 0.8]), 0, 1)
    else:
        out = a * mul + lift
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def overlay_zones(img):
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x0, y0, x1, y1 in UI_ZONES:
        d.rectangle([x0 * w, y0 * h, x1 * w - 1, y1 * h - 1], fill=(220, 40, 40, 60), outline=(220, 40, 40, 160))
    d.rectangle([0.06 * w, 0.10 * h, 0.86 * w, 0.78 * h], outline=(255, 255, 255, 110), width=2)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def tc(frame, fps):
    s = frame / fps
    return f"{int(s // 60):02d}:{s % 60:05.2f}"


def panel(frame_img, shot, meta):
    fps = meta["fps"]
    f = ImageFont.truetype(FONT, 15)
    fb = ImageFont.truetype(FONT_B, 17)
    w = frame_img.width
    pad = 14
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    blocks = [("ACTION", shot["action"]), ("PERFORMANCE", shot.get("performance", "")),
              ("CAMERA", f"{shot['size']} | {shot['lens']} mm | {shot.get('camera_move', 'Locked off')}"),
              ("SOUND", shot.get("sound", ""))]
    body = []
    for label, text in blocks:
        if text:
            body.append((label, wrap(scratch, text, f, w - 2 * pad)))
    cap_h = 52 + sum(22 + 19 * len(lines) for _, lines in body) + pad
    out = Image.new("RGB", (w, frame_img.height + cap_h), (24, 22, 21))
    out.paste(overlay_zones(frame_img), (0, 0))
    d = ImageDraw.Draw(out)
    y = frame_img.height + pad
    start, end = shot["start"], shot["start"] + shot["frames"]
    d.text((pad, y), f"{meta['id']} {shot['id']}   {tc(start, fps)}-{tc(end, fps)}   ({shot['frames']} f)",
           font=fb, fill=(245, 235, 220))
    y += 30
    for label, lines in body:
        d.text((pad, y), label, font=ImageFont.truetype(FONT_B, 13), fill=(214, 150, 110))
        y += 20
        for line in lines:
            d.text((pad, y), line, font=f, fill=(225, 220, 212))
            y += 19
        y += 2
    return out


def burn(img, text):
    img = img.copy()
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_B, 16)
    d.rectangle([8, 8, 16 + d.textlength(text, font=f), 32], fill=(0, 0, 0))
    d.text((12, 10), text, font=f, fill=(255, 255, 255))
    return img


# ----------------------------------------------------------- temp sync sound

def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def synth(kind, seed):
    n = lambda s: int(SR * s)
    t = lambda s: np.arange(n(s)) / SR
    if kind == "clop":
        x = np.sin(2 * math.pi * 150 * t(0.12)) * env(n(0.12), 0.002, 0.03) + 0.4 * lowpass(noise(n(0.12), seed), 6) * env(n(0.12), 0.001, 0.01)
    elif kind == "knock":
        x = np.sin(2 * math.pi * 320 * t(0.08)) * env(n(0.08), 0.001, 0.02)
    elif kind in ("thud", "pat"):
        f0 = 90 if kind == "thud" else 240
        x = np.sin(2 * math.pi * f0 * t(0.1)) * env(n(0.1), 0.002, 0.025) * (1 if kind == "thud" else 0.5)
    elif kind in ("sniff", "rustle", "crackle", "scrape"):
        dur = {"sniff": 0.35, "rustle": 0.4, "crackle": 1.2, "scrape": 0.5}[kind]
        x = noise(n(dur), seed)
        if kind == "sniff":
            x = (x - lowpass(x, 12)) * np.sin(np.linspace(0, math.pi, n(dur))) * 0.5
        elif kind == "crackle":
            x = x * (np.random.default_rng(seed).random(n(dur)) > 0.995) * 0.8
        else:
            x = lowpass(x, 4) * np.sin(np.linspace(0, math.pi, n(dur))) * 0.35
    elif kind == "munch":
        x = np.concatenate([lowpass(noise(n(0.06), seed + i), 3) * env(n(0.06), 0.002, 0.02) * 0.6 for i in range(2)])
    elif kind == "creak":
        f = np.linspace(180, 140, n(0.35))
        x = np.sign(np.sin(2 * math.pi * np.cumsum(f) / SR)) * env(n(0.35), 0.02, 0.15) * 0.15
    elif kind == "squeak":
        f = np.linspace(1300, 1900, n(0.12))
        x = np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n(0.12), 0.005, 0.05) * 0.35
    elif kind in ("grunt",):
        f = np.linspace(170, 120, n(0.3))
        x = (np.sin(2 * math.pi * np.cumsum(f) / SR) + 0.3 * lowpass(noise(n(0.3), seed), 8)) * env(n(0.3), 0.02, 0.12) * 0.5
    elif kind == "tick":
        x = np.sin(2 * math.pi * 1800 * t(0.03)) * env(n(0.03), 0.001, 0.006) * 0.5
    elif kind == "whoosh":
        x = lowpass(noise(n(0.35), seed), 10) * np.sin(np.linspace(0, math.pi, n(0.35))) ** 2 * 0.6
    elif kind == "latch":
        x = np.concatenate([np.sin(2 * math.pi * 900 * t(0.04)) * env(n(0.04), 0.001, 0.008), np.zeros(n(0.05)),
                            np.sin(2 * math.pi * 700 * t(0.05)) * env(n(0.05), 0.001, 0.01)]) * 0.6
    elif kind in ("sting", "chord"):
        dur = 1.2 if kind == "sting" else 2.0
        x = sum(np.sin(2 * math.pi * f0 * t(dur)) for f0 in (392, 494, 587)) / 3 * env(n(dur), 0.05, 0.5) * 0.35
    else:
        x = np.zeros(1)
    return x.astype(np.float32)


def soundtrack(meta, path, total_frames):
    total = int(SR * total_frames / meta["fps"]) + SR // 2
    mix = np.zeros(total, dtype=np.float32)
    for i, shot in enumerate(meta["shots"]):
        for j, cue in enumerate(shot.get("cues", [])):
            x = synth(cue["type"], i * 31 + j)
            a = int(cue["t"] * SR)
            mix[a:a + len(x)] += x[: max(0, total - a)]
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.8), -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


# ----------------------------------------------------------- main

def main():
    shots_path, render_dir, root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    meta = json.loads(shots_path.read_text())
    fps, tag = meta["fps"], f"{meta['id']}_{meta['title']}"
    ver = meta.get("version", "v001")
    boards = root / "03_STORYBOARDS" / tag
    boards.mkdir(parents=True, exist_ok=True)
    (root / "04_ANIMATICS").mkdir(parents=True, exist_ok=True)
    (root / "02_PREPRODUCTION" / "shotlists").mkdir(parents=True, exist_ok=True)

    panels = []
    for shot in meta["shots"]:
        g = shot.get("grade", "day")
        for suffix in ("", "_end"):
            src = render_dir / f"{shot['id']}{suffix}.png"
            if not src.exists():
                continue
            p = panel(grade(Image.open(src), g), dict(shot, id=shot["id"] + (" (end of move)" if suffix else "")), meta)
            out = boards / f"{tag}_{shot['id']}{suffix}_{ver}.jpg"
            p.save(out, quality=88)
            panels.append(p)

    cols = 4
    cw = panels[0].width
    rows = math.ceil(len(panels) / cols)
    rh = max(p.height for p in panels)
    head = 70
    sheet = Image.new("RGB", (cols * (cw + 12) + 12, head + rows * (rh + 12) + 12), (14, 13, 12))
    d = ImageDraw.Draw(sheet)
    total = sum(s["frames"] for s in meta["shots"])
    d.text((16, 14), f"{meta['id']} \"{meta['title']}\" storyboard {ver}  |  {tc(total, fps)}  |  9:16 blockout (Workbench), proxies not final designs",
           font=ImageFont.truetype(FONT_B, 22), fill=(245, 235, 220))
    d.text((16, 44), "Red zones: approximate platform UI overlays. White box: keep faces and key action inside.",
           font=ImageFont.truetype(FONT, 16), fill=(200, 190, 180))
    for i, p in enumerate(panels):
        sheet.paste(p, (12 + (i % cols) * (cw + 12), head + 12 + (i // cols) * (rh + 12)))
    sheet.save(boards / f"{tag}_contact_sheet_{ver}.jpg", quality=88)

    lines = [f"# {meta['id']} \"{meta['title']}\" shot list {ver}", "",
             f"Generated from `02_PREPRODUCTION/shots/{shots_path.name}`. {len(meta['shots'])} shots, {total} frames at {fps} fps ({total / fps:.1f} s), 1080 x 1920.", "",
             "| Shot | In | Out | Frames | Size | Lens | Move | Light | Action |", "|---|---|---|---|---|---|---|---|---|"]
    for s in meta["shots"]:
        lines.append(f"| {s['id']} | {tc(s['start'], fps)} | {tc(s['start'] + s['frames'], fps)} | {s['frames']} | {s['size']} | {s['lens']} mm | "
                     f"{s.get('camera_move', 'Locked off')} | {s.get('grade', 'day')} | {s['action']} |")
    (root / "02_PREPRODUCTION" / "shotlists" / f"{tag}_shotlist_{ver}.md").write_text("\n".join(lines) + "\n")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        segs = []
        for k, shot in enumerate(meta["shots"]):
            g = shot.get("grade", "day")
            label = f"{meta['id']} {shot['id']}"
            seq = render_dir / f"{shot['id']}_seq"
            seg = tmp / f"seg{k:02d}.mp4"
            if seq.is_dir() and any(seq.iterdir()):
                fdir = tmp / f"f{k:02d}"
                fdir.mkdir()
                frames = sorted(seq.glob("*.png"))
                step = shot["frames"] / len(frames)
                for i in range(shot["frames"]):
                    src = frames[min(len(frames) - 1, int(i / step))]
                    burn(grade(Image.open(src), g), label).save(fdir / f"{i:04d}.png")
                cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(fdir / "%04d.png")]
            else:
                still = tmp / f"still{k:02d}.png"
                burn(grade(Image.open(render_dir / f"{shot['id']}.png"), g), label).save(still)
                cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(fps), "-i", str(still),
                       "-frames:v", str(shot["frames"])]
            subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps), str(seg)], check=True)
            segs.append(seg)
        (tmp / "list.txt").write_text("".join(f"file '{s}'\n" for s in segs))
        wav = tmp / "temp.wav"
        soundtrack(meta, wav, total)
        out = root / "04_ANIMATICS" / f"{tag}_animatic_{ver}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                        "-i", str(wav), "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print("built", tag, len(panels), "panels")


main()
