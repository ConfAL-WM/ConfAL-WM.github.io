#!/usr/bin/env python3
"""Build the project-page confidence gallery (50 tasks x 6 videos, dual space).

Renders, per prescreen episode, six synchronized H.264 clips for each space:

  pixel space (view = "pixel")
  01.mp4  ground-truth frame            (dataset frames, aligned to pred range)
  02.mp4  predicted frame               (EVAC-v1 rollout frames)
  03.mp4  predicted latent error        (|latent_pred - latent_gt| pooled to [T,20,32], magma)
  04.mp4  predicted confidence          (C3 conf_map, RdBu)
  05.mp4  predicted risk                (1 - conf, inferno)
  06.mp4  risk overlay on prediction

  latent space (view = "latent")  — same 03/04/05; columns 1/2/6 swap to:
  01l.mp4 GT latent magnitude      (mean |z_gt| over channels, viridis)
  02l.mp4 predicted latent magnitude (mean |z_pred|, viridis)
  06l.mp4 risk overlay on the pred latent magnitude map

The map videos render the 20x32 grid nearest-upsampled to a crisp block grid at
a higher output resolution (no blurry bilinear smearing).

Colorization / overlay / pooling mirror the repo's
`eval/al_results/visualize_val_results.py` and
`eval/confidence_eval/core/io_utils.py`.

Output tree (matches index.html):
  assets/confidence/group-XX/task-XX/{01..06}.mp4 (+ 01l/02l/06l.mp4)
  assets/confidence/task_index.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path("/share/project/robocoin/hywu/lx/EVAC-C3")
PRED_ROOT = REPO / "al_runs/robotwin_al/pool_scores/pred/task_prescreen"
SCORE_ROOT = REPO / "al_runs/robotwin_al/pool_scores/c3_task_prescreen_scores"
DATASET_ROOT = Path("/share/project/robocoin/hywu/lx/datasets/RoboTwin2.0/aloha-agilex_rand_500")
OUT_ROOT = Path(__file__).resolve().parents[1] / "assets/confidence"

HW = (20, 32)  # conf_map spatial shape
FPS = 10


# ---------------------------------------------------------------- repo-identical helpers
def colorize(arr: np.ndarray, cmap_name: str, vmin: float, vmax: float) -> np.ndarray:
    """visualize_val_results._colorize."""
    x = np.asarray(arr, dtype=np.float32)
    if not np.isfinite(vmax) or vmax <= vmin:
        vmax = vmin + 1.0
    x = np.clip((x - vmin) / (vmax - vmin), 0.0, 1.0)
    rgb = plt.get_cmap(cmap_name)(x)[..., :3]
    return (rgb * 255.0).round().astype(np.uint8)


def error_vmax(value_map: np.ndarray | None, percentile: float = 98.0) -> float:
    finite = np.asarray(value_map, dtype=np.float32)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return 1.0
    vmax = float(np.percentile(finite, percentile))
    return vmax if np.isfinite(vmax) and vmax > 0 else 1.0


def resize_scalar(arr: np.ndarray, size_hw: tuple[int, int]) -> np.ndarray:
    h, w = size_hw
    img = Image.fromarray(np.asarray(arr, dtype=np.float32), mode="F")
    return np.asarray(img.resize((w, h), Image.Resampling.BILINEAR), dtype=np.float32)


def overlay_risk(base: np.ndarray, risk_hw: np.ndarray, alpha_scale: float = 0.70) -> np.ndarray:
    """visualize_val_results._overlay_risk."""
    risk_up = np.clip(resize_scalar(risk_hw, base.shape[:2]), 0.0, 1.0)
    heat = colorize(risk_up, cmap_name="inferno", vmin=0.0, vmax=1.0).astype(np.float32)
    alpha = (np.power(risk_up, 0.6) * float(alpha_scale))[..., None]
    out = alpha * heat + (1.0 - alpha) * base.astype(np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)


def adaptive_avg_pool2d_np(array_2d: np.ndarray, output_hw: tuple[int, int]) -> np.ndarray:
    """io_utils._adaptive_avg_pool2d_np."""
    in_h, in_w = array_2d.shape
    out_h, out_w = output_hw
    out = np.zeros((out_h, out_w), dtype=np.float32)
    for i in range(out_h):
        h0 = int(np.floor(i * in_h / out_h))
        h1 = max(int(np.ceil((i + 1) * in_h / out_h)), h0 + 1)
        for j in range(out_w):
            w0 = int(np.floor(j * in_w / out_w))
            w1 = max(int(np.ceil((j + 1) * in_w / out_w)), w0 + 1)
            out[i, j] = float(np.mean(array_2d[h0:h1, w0:w1]))
    return out


def latent_error_map(pred_latent: np.ndarray, gt_latent: np.ndarray, n: int) -> np.ndarray:
    """io_utils.compute_latent_oracle_error_map (mean over channels, pooled to HW)."""
    pred = np.asarray(pred_latent, dtype=np.float32)[:n]
    gt = np.asarray(gt_latent, dtype=np.float32)[:n]
    mae = np.mean(np.abs(pred - gt), axis=1)  # [T,H,W]
    return np.stack([adaptive_avg_pool2d_np(f, HW) for f in mae], axis=0)


def latent_magnitude_map(latent: np.ndarray, n: int) -> np.ndarray:
    """visualize_val_results._load_latent_maps: mean |z| over channels."""
    z = np.asarray(latent, dtype=np.float32)[:n]
    return np.mean(np.abs(z), axis=1).astype(np.float32)  # [T,H,W]


# ---------------------------------------------------------------- frame io
def load_pred_frames(ep_dir: Path) -> np.ndarray:
    files = sorted((ep_dir / "pred_frames").glob("frame_*.jpg"))
    if not files:
        raise FileNotFoundError(f"no pred frames in {ep_dir/'pred_frames'}")
    return np.stack([np.asarray(Image.open(f).convert("RGB")) for f in files], axis=0)


def load_gt_frames(source_path: Path, n_previous: int, n_frames: int) -> np.ndarray:
    files = sorted((source_path / "frames").glob("frame_*.jpg"))
    if not files:
        raise FileNotFoundError(f"no gt frames in {source_path/'frames'}")
    raw = files[n_previous : n_previous + n_frames]
    return np.stack([np.asarray(Image.open(f).convert("RGB")) for f in raw], axis=0)


def upscale_map(color_map: np.ndarray, target_hw: tuple[int, int]) -> np.ndarray:
    """Nearest-neighbor upscale of a colorized [T,20,32,3] map -> crisp patch blocks."""
    th, tw = target_hw
    frames = []
    for f in color_map:
        img = Image.fromarray(f).resize((tw, th), Image.Resampling.NEAREST)
        frames.append(np.asarray(img))
    return np.stack(frames, axis=0)


def write_video(frames: np.ndarray, out_path: Path, width: int, crf: int = 22) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".tmp.mp4")
    h, w = frames.shape[1:3]
    scale = f"scale={width}:-2:flags=lanczos" if w != width else "null"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
        "-i", "-",
        "-an", "-vf", scale,
        "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(tmp),
    ]
    proc = subprocess.run(cmd, input=frames.tobytes(), capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path}: {proc.stderr.decode()[:500]}")
    shutil.move(str(tmp), str(out_path))


# ---------------------------------------------------------------- per-episode render
def render_episode(ep_id: str, out_dir: Path, width: int, n_previous_default: int = 4) -> dict:
    meta = json.loads((PRED_ROOT / ep_id / "meta.json").read_text())
    score_meta = json.loads((SCORE_ROOT / ep_id / "meta.json").read_text())

    pred = load_pred_frames(PRED_ROOT / ep_id)
    conf = np.load(SCORE_ROOT / ep_id / "conf_map.npy").astype(np.float32)
    lp = np.load(PRED_ROOT / ep_id / "latent_pred.npy")
    lg = np.load(PRED_ROOT / ep_id / "latent_gt.npy")

    n_previous = int(score_meta.get("n_condition_frames", n_previous_default))
    source = Path(score_meta.get("source_path") or meta.get("source_path"))
    if not source.is_absolute():
        source = DATASET_ROOT / source.name
    if not (source / "frames").is_dir():
        cand = DATASET_ROOT / f"{meta['task_name']}-{ep_id}-0"
        if (cand / "frames").is_dir():
            source = cand
        else:
            raise FileNotFoundError(f"GT frames not found for {ep_id} (tried {source})")

    gt = load_gt_frames(source, n_previous, pred.shape[0])
    n = min(pred.shape[0], gt.shape[0], conf.shape[0], lp.shape[0], lg.shape[0])
    pred, gt, conf, lp, lg = pred[:n], gt[:n], conf[:n], lp[:n], lg[:n]
    if gt.shape[1:3] != pred.shape[1:3]:
        gt = np.stack(
            [np.asarray(Image.fromarray(f).resize((pred.shape[2], pred.shape[1]), Image.Resampling.BILINEAR)) for f in gt],
            axis=0,
        )

    # maps
    err = latent_error_map(lp, lg, n)
    err_vmax = error_vmax(err)
    risk = 1.0 - conf
    pred_lat = latent_magnitude_map(lp, n)
    gt_lat = latent_magnitude_map(lg, n)
    lat_vmax = error_vmax(np.concatenate([pred_lat.reshape(-1), gt_lat.reshape(-1)]))

    target_hw = (pred.shape[1], pred.shape[2])  # (320, 512)

    def map_views(colorized: np.ndarray) -> np.ndarray:
        return upscale_map(colorized, target_hw)

    err_c = np.stack([colorize(f, "magma", 0.0, err_vmax) for f in err], axis=0)
    conf_c = np.stack([colorize(f, "RdBu", 0.0, 1.0) for f in conf], axis=0)
    risk_c = np.stack([colorize(f, "inferno", 0.0, 1.0) for f in risk], axis=0)
    gt_lat_c = np.stack([colorize(f, "viridis", 0.0, lat_vmax) for f in gt_lat], axis=0)
    pred_lat_c = np.stack([colorize(f, "viridis", 0.0, lat_vmax) for f in pred_lat], axis=0)

    # pixel-space overlay uses bilinear risk over the pred frame (repo behavior)
    overlay_pixel = np.stack([overlay_risk(p, r) for p, r in zip(pred, risk)], axis=0)
    # latent-space overlay: crisp block-grid risk over the block-upsampled latent map
    pred_lat_up = upscale_map(pred_lat_c, target_hw)
    risk_up_raw = np.stack(
        [np.asarray(Image.fromarray(np.uint8(r * 255)).resize((target_hw[1], target_hw[0]), Image.Resampling.NEAREST), dtype=np.float32) / 255.0 for r in risk],
        axis=0,
    )
    heat_up = np.stack([colorize(r, "inferno", 0.0, 1.0).astype(np.float32) for r in risk_up_raw], axis=0)
    alpha = (np.power(risk_up_raw, 0.6) * 0.70)[..., None]
    overlay_latent = np.clip(alpha * heat_up + (1.0 - alpha) * pred_lat_up.astype(np.float32), 0, 255).astype(np.uint8)

    views = {
        "01": (gt, 26),
        "02": (pred, 26),
        "03": (map_views(err_c), 27),
        "04": (map_views(conf_c), 27),
        "05": (map_views(risk_c), 27),
        "06": (overlay_pixel, 26),
        "01l": (upscale_map(gt_lat_c, target_hw), 27),
        "02l": (pred_lat_up, 27),
        "06l": (overlay_latent, 27),
    }
    for key, (frames, crf) in views.items():
        write_video(frames, out_dir / f"{key}.mp4", width, crf=crf)

    return {"episode_id": ep_id, "task_name": meta["task_name"], "frames": int(n), "gt_source": str(source)}


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=768, help="output video width in px")
    ap.add_argument("--only", type=str, default="", help="comma-separated task names to rebuild")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    episodes = sorted(p.name for p in PRED_ROOT.iterdir() if p.is_dir() and (p / "pred_frames").is_dir())
    tasks = sorted({json.loads((PRED_ROOT / e / "meta.json").read_text())["task_name"] for e in episodes})
    by_task: dict[str, str] = {}
    for e in episodes:
        t = json.loads((PRED_ROOT / e / "meta.json").read_text())["task_name"]
        by_task.setdefault(t, e)

    only = {x for x in args.only.split(",") if x}
    index = []
    for i, task in enumerate(tasks):
        group = f"group-{i // 5 + 1:02d}"
        slot = f"task-{i + 1:02d}"
        entry = {"id": slot, "group": group, "task": task, "episode": by_task[task]}
        index.append(entry)
        if only and task not in only:
            continue
        out_dir = OUT_ROOT / group / slot
        if args.dry_run:
            print(f"[dry] {group}/{slot} <- {by_task[task]}")
            continue
        info = render_episode(by_task[task], out_dir, args.width)
        entry.update({k: info[k] for k in ("frames", "gt_source")})
        print(f"[ok] {group}/{slot} <- {by_task[task]} ({info['frames']} frames)", flush=True)

    if not args.dry_run:
        OUT_ROOT.mkdir(parents=True, exist_ok=True)
        (OUT_ROOT / "task_index.json").write_text(json.dumps(index, indent=2))
        print(f"wrote {OUT_ROOT / 'task_index.json'} with {len(index)} tasks")


if __name__ == "__main__":
    sys.exit(main())
