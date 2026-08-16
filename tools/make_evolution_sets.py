#!/usr/bin/env python3
"""Build the project-page qualitative-evolution video sets.

For each paper episode in `1_paper_figure/al_progression_demos/episodes/`, copy +
re-encode the five synchronized clips into:

  assets/evolution/<id>/{gt,base,v1,frame,frame_patch}.mp4

Episode ids follow ASSET_PREPARATION.md (ep130, ep294, ...). The ten available
demos fill the six paper slots plus four extras; the mapping is written to
assets/evolution/episode_index.json.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/share/project/robocoin/hywu/lx/EVAC-C3")
SRC = REPO / "1_paper_figure/al_progression_demos/episodes"
OUT_ROOT = Path(__file__).resolve().parents[1] / "assets/evolution"

# Paper slot -> full episode id (first six are the paper's headline episodes).
SLOTS = {
    "ep130": "place_burger_fries_aloha-agilex_randomized_500_ep130",
    "ep294": "place_empty_cup_aloha-agilex_randomized_500_ep294",
    "ep282": "put_object_cabinet_aloha-agilex_randomized_500_ep282",
    "ep325": "stack_blocks_two_aloha-agilex_randomized_500_ep325",
    "ep087": "stack_bowls_three_aloha-agilex_randomized_500_ep087",
    "ep310": "turn_switch_aloha-agilex_randomized_500_ep310",
    "extra-01": "blocks_ranking_size_aloha-agilex_randomized_500_ep164",
    "extra-02": "shake_bottle_aloha-agilex_randomized_500_ep295",
    "extra-03": "hanging_mug_aloha-agilex_randomized_500_ep064",
    "extra-04": "dump_bin_bigbin_aloha-agilex_randomized_500_ep276",
}

# slot file -> source file inside the episode folder
FILE_MAP = {
    "gt.mp4": ("ground_truth", "gt_video.mp4"),
    "base.mp4": ("BASE_EVAC", "pred_video.mp4"),
    "v1.mp4": ("v1", "pred_video.mp4"),
    "frame.mp4": ("v2_frame", "pred_video.mp4"),
    "frame_patch.mp4": ("v2_frame_patch", "pred_video.mp4"),
}


def reencode(src: Path, dst: Path, width: int = 480) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp.mp4")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
        "-an", "-vf", f"scale={width}:-2:flags=bicubic",
        "-c:v", "libx264", "-crf", "25", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp),
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {src}: {proc.stderr.decode()[:300]}")
    shutil.move(str(tmp), str(dst))


def main() -> None:
    index = []
    for slot, ep in SLOTS.items():
        ep_dir = SRC / ep
        if not ep_dir.is_dir():
            print(f"[skip] missing {ep}", file=sys.stderr)
            continue
        for out_name, (sub, fname) in FILE_MAP.items():
            src = ep_dir / sub / fname
            dst = OUT_ROOT / slot / out_name
            reencode(src, dst)
        index.append({"id": slot, "episode": ep, "task": ep.rsplit("_aloha", 1)[0]})
        print(f"[ok] {slot} <- {ep}", flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "episode_index.json").write_text(json.dumps(index, indent=2))
    print(f"wrote {len(index)} episode sets")


if __name__ == "__main__":
    sys.exit(main())
