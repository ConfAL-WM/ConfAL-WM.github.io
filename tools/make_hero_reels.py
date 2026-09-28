#!/usr/bin/env python3
"""Build three frame-aligned, 15-second hero reels from the chapter 3 gallery.

Run with Python and ffmpeg on PATH (or with imageio-ffmpeg installed).
Each task contributes its middle 30 frames at the source rate of 10 fps.
"""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = (1, 3, 9, 12, 23)
VIEWS = {"ground-truth": "01", "risk": "05", "overlay": "06"}
FPS = 10
CLIP_FRAMES = 30


def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    index = json.loads((ROOT / "assets/confidence/task_index.json").read_text())
    tasks = [index[i - 1] for i in TASKS]
    out = ROOT / "assets/video/hero"
    out.mkdir(parents=True, exist_ok=True)
    clips = []
    for task in tasks:
        start = (task["frames"] - CLIP_FRAMES) // 2
        assert start >= 0
        clips.append({"task": task["task"], "directory": f"assets/confidence/{task['group']}/{task['id']}",
                      "start_frame": start, "end_frame_exclusive": start + CLIP_FRAMES})
    for view, column in VIEWS.items():
        args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
        filters = []
        for i, clip in enumerate(clips):
            args += ["-i", str(ROOT / clip["directory"] / f"{column}.mp4")]
            filters.append(f"[{i}:v]trim=start_frame={clip['start_frame']}:end_frame={clip['end_frame_exclusive']},"
                           f"setpts=N/({FPS}*TB),scale=768:480,setsar=1[v{i}]")
        filters.append("".join(f"[v{i}]" for i in range(len(clips))) + "concat=n=5:v=1:a=0[out]")
        args += ["-filter_complex", ";".join(filters), "-map", "[out]", "-an", "-c:v", "libx264",
                 "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
                 "-g", "10", "-keyint_min", "10", "-sc_threshold", "0", "-movflags", "+faststart",
                 str(out / f"{view}.mp4")]
        subprocess.run(args, check=True)
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(out / f"{view}.mp4"),
                        "-frames:v", "1", "-q:v", "3", str(out / f"{view}-poster.jpg")], check=True)
        print(f"Built {view}.mp4", flush=True)
    (out / "clips.json").write_text(json.dumps({"fps": FPS, "duration_seconds": 15,
                                               "source_columns": VIEWS, "clips": clips}, indent=2) + "\n")


if __name__ == "__main__":
    main()
